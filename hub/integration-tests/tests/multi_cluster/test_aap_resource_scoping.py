"""Offline checks for AAP hook and agent naming on a shared controller."""

import json
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest

pytestmark = pytest.mark.skipif(shutil.which("helm") is None, reason="helm CLI not available")

HUB = next(parent for parent in Path(__file__).resolve().parents if parent.name == "hub")
NETWORK_CHART = HUB / "helm" / "charts" / "network"

_ENV_ENTRY = re.compile(r'- name: (\S+)\n\s+value: "([^"]*)"')


def render_network(namespace, show_only, enabled=True):
    command = [
        "helm",
        "template",
        "hub",
        str(NETWORK_CHART),
        "--namespace",
        namespace,
        "--show-only",
        show_only,
        "--set",
        f"aapCredential.enabled={str(enabled).lower()}",
        "--set",
        "global.frontendAuth.enabled=false",
        "--set",
        "global.routes.enabled=false",
    ]
    return subprocess.run(command, capture_output=True, text=True, check=True).stdout


def agent_environment(namespace, enabled=True):
    rendered = render_network(namespace, "templates/agent-service.yaml", enabled=enabled)
    return dict(_ENV_ENTRY.findall(rendered))


def hook_script(namespace):
    rendered = render_network(namespace, "templates/aap-credential-script-cm.yaml")
    return textwrap.dedent(rendered.split("setup.sh: |\n", 1)[1])


@pytest.mark.parametrize("namespace", ["hub-team-a", "hub-another"])
def test_hook_and_agent_share_scoped_names(namespace):
    environment = agent_environment(namespace)
    prefix = namespace + "-"
    assert environment["AAP_RESOURCE_PREFIX"] == prefix
    assert environment["AAP_LIGHTSPEED_TEMPLATE"] == prefix + "lightspeed-runner"
    assert environment["GITEA_PROJECT_NAME"] == prefix + "lightspeed-generated"
    hook = hook_script(namespace)
    subprocess.run(["bash", "-n"], input=hook, text=True, check=True)
    assert f'RESOURCE_PREFIX="{prefix}"' in hook
    assert 'PROJ_NAME="${RESOURCE_PREFIX}lightspeed-generated"' in hook
    assert 'CRED_NAME="${RESOURCE_PREFIX}hub-remediation"' in hook
    assert 'MC_CRED_NAME="${RESOURCE_PREFIX}rhacm-hub"' in hook
    assert 'CRED_TYPE_NAME="${RESOURCE_PREFIX}RHACM Cluster Proxy"' in hook


def test_unmanaged_aap_keeps_existing_names():
    environment = agent_environment("hub", enabled=False)
    assert environment["AAP_RESOURCE_PREFIX"] == ""
    assert environment["AAP_LIGHTSPEED_TEMPLATE"] == "lightspeed-runner"
    assert environment["GITEA_PROJECT_NAME"] == "lightspeed-generated"


# Execute the actual rendered hook functions against a local shell API double.
# IDs 1/2 and credential 7 belong to a different hub; 101/102 and 20 are ours.
_AAP_DOUBLE = r"""
aap_get() {
  case "$1" in
    /credentials/\?name=*) echo '{"results":[{"id":20}]}' ;;
    /projects/\?name=*) echo '{"results":[{"id":35}]}' ;;
    /job_templates/\?name=lightspeed-runner) echo '{"results":[{"id":1}]}' ;;
    /job_templates/\?name=restart-nginx) echo '{"results":[{"id":2}]}' ;;
    /job_templates/\?name="${RESOURCE_PREFIX}lightspeed-runner")
      if [ -f "$TEST_STATE/1" ]; then echo '{"results":[{"id":101}]}'; else echo '{"results":[]}'; fi ;;
    /job_templates/\?name="${RESOURCE_PREFIX}restart-nginx")
      if [ -f "$TEST_STATE/2" ]; then echo '{"results":[{"id":102}]}'; else echo '{"results":[]}'; fi ;;
    /job_templates/10[12]/credentials/\?page_size=200)
      local template_id
      template_id=$(echo "$1" | cut -d/ -f3)
      if [ -f "$TEST_STATE/credential-$template_id" ]; then
        echo '{"results":[{"id":7},{"id":20}]}'
      else
        echo '{"results":[{"id":7}]}'
      fi ;;
    *) echo "Unexpected GET $1" >&2; return 1 ;;
  esac
}
aap_post() {
  printf '%s\t%s\n' "$1" "$2" >> "$TEST_STATE/writes"
  case "$1" in
    /job_templates/[12]/copy/) touch "$TEST_STATE/$(echo "$1" | cut -d/ -f3)" ;;
    /job_templates/10[12]/credentials/)
      if [ "$2" = '{"id": 20}' ]; then
        local credential_state="$TEST_STATE/credential-$(echo "$1" | cut -d/ -f3)"
        [ ! -f "$credential_state" ] || { echo 'Duplicate credential rejected' >&2; return 1; }
        touch "$credential_state"
      fi ;;
    *) echo "Refusing shared-resource mutation: $1" >&2; return 1 ;;
  esac
}
aap_patch() {
  [ "$1" = /job_templates/102/ ] || return 1
  printf '%s\t%s\n' "$1" "$2" >> "$TEST_STATE/writes"
  echo '{}'
}
"""


_COPY_AND_SEED = """
EFFECTIVE_CRED_NAME="${RESOURCE_PREFIX}hub-remediation"
PROJ_NAME="${RESOURCE_PREFIX}lightspeed-generated"
copy_templates_with_credential "$EFFECTIVE_CRED_NAME" "$SOURCE_BASE_TMPL" restart-nginx
copy_templates_with_credential "$EFFECTIVE_CRED_NAME" "$SOURCE_BASE_TMPL" restart-nginx
upsert_template_for_playbook restart-nginx.yaml
"""


@pytest.mark.parametrize("namespace", ["hub-team-a", "hub-another"])
def test_hook_copies_without_mutating_shared_templates(namespace, tmp_path):
    hook = hook_script(namespace)
    definitions = hook.split('\nif [ "$MULTICLUSTER_ENABLED" = "true" ]; then')[0]
    execution = subprocess.run(
        ["bash", "-c", definitions + _AAP_DOUBLE + _COPY_AND_SEED],
        env={"PATH": "/usr/bin:/bin", "AAP_VERIFY_SSL": "false", "TEST_STATE": str(tmp_path)},
        capture_output=True,
        text=True,
    )
    assert execution.returncode == 0, execution.stdout + execution.stderr
    writes = [line.split("\t", 1) for line in (tmp_path / "writes").read_text().splitlines()]
    copies = [json.loads(payload)["name"] for endpoint, payload in writes if endpoint.endswith("/copy/")]
    assert copies == [namespace + "-lightspeed-runner", namespace + "-restart-nginx"]
    attachments = [endpoint for endpoint, payload in writes if json.loads(payload) == {"id": 20}]
    assert attachments == ["/job_templates/101/credentials/", "/job_templates/102/credentials/"]
    for endpoint, payload in writes:
        if endpoint.endswith("/credentials/"):
            credential = json.loads(payload)
            assert credential == {"id": 7, "disassociate": True} or credential == {"id": 20}
    patches = [json.loads(payload) for endpoint, payload in writes if endpoint == "/job_templates/102/"]
    assert patches == [{"playbook": "playbooks/restart-nginx.yaml", "ask_variables_on_launch": True, "project": 35}]
