import json

import pytest

from agent_service.kafka.alerts import ALERT_TOPICS, parse_kafka_message


@pytest.mark.parametrize("topic", sorted(ALERT_TOPICS))
class TestAlertTopics:
    def test_json_with_message_field(self, topic):
        payload = {
            "message": "nginx CrashLoopBackOff in namespace dark-noc-edge",
            "severity": "high",
            "namespace": "dark-noc-edge",
        }
        result = parse_kafka_message(topic, json.dumps(payload).encode())

        assert result == json.dumps(payload, separators=(",", ":"), sort_keys=True)

    def test_plain_text(self, topic):
        result = parse_kafka_message(topic, b"nginx CrashLoopBackOff in namespace prod")

        assert result == "nginx CrashLoopBackOff in namespace prod"


class TestJsonWithoutMessage:
    def test_serializes_full_object(self):
        payload = {
            "severity": "high",
            "source": "edge-01",
            "component": "nginx",
        }
        result = parse_kafka_message("system-alerts", json.dumps(payload).encode())

        assert result == json.dumps(payload, separators=(",", ":"), sort_keys=True)

    def test_empty_message_field_preserves_full_payload(self):
        payload = {"message": "   ", "severity": "low"}
        result = parse_kafka_message("noc-alerts", json.dumps(payload).encode())

        assert result == json.dumps(payload, separators=(",", ":"), sort_keys=True)

    def test_json_array_serializes(self):
        payload = [{"alert": "OOMKilled"}, {"alert": "CrashLoopBackOff"}]
        result = parse_kafka_message("system-alerts", json.dumps(payload).encode())

        assert result == json.dumps(payload, separators=(",", ":"))


class TestPlainTextAndEdgeCases:
    def test_strips_surrounding_whitespace(self):
        result = parse_kafka_message("system-alerts", b"  nginx pod failed  \n")

        assert result == "nginx pod failed"

    def test_empty_payload_returns_none(self):
        assert parse_kafka_message("system-alerts", b"") is None
        assert parse_kafka_message("system-alerts", b"   ") is None

    def test_invalid_utf8_returns_none(self):
        assert parse_kafka_message("system-alerts", b"\xff\xfe invalid") is None

    def test_invalid_json_falls_back_to_plain_text(self):
        result = parse_kafka_message("system-alerts", b"{not-json: value")

        assert result == "{not-json: value"


class TestUnknownTopic:
    def test_unknown_topic_returns_none(self):
        result = parse_kafka_message("nginx-logs", b'{"message":"should be skipped"}')

        assert result is None
