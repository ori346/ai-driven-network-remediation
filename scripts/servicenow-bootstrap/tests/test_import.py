"""Smoke test: verify the package can be imported."""


def test_import() -> None:
    import servicenow_bootstrap

    assert servicenow_bootstrap.__version__ == "0.1.0"


def test_import_classes() -> None:
    from servicenow_bootstrap import (
        ServiceNowAPIAutomation,
        ServiceNowUserAutomation,
        get_env_var,
    )

    assert callable(get_env_var)
    assert ServiceNowAPIAutomation is not None
    assert ServiceNowUserAutomation is not None
