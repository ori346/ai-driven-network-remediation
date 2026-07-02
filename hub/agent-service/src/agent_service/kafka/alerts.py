import json

from loguru import logger

ALERT_TOPICS = frozenset({"system-alerts", "noc-alerts"})


def _parse_alert_payload(text: str) -> str | None:
    stripped = text.strip()
    if not stripped:
        return None

    if stripped.startswith("{") or stripped.startswith("["):
        try:
            parsed = json.loads(stripped)
        except json.JSONDecodeError:
            return stripped

        return json.dumps(parsed, separators=(",", ":"), sort_keys=True)

    return stripped


def parse_kafka_message(topic: str, value: bytes) -> str | None:
    """Normalize a Kafka alert payload into a LangGraph raw_event string."""
    if topic not in ALERT_TOPICS:
        logger.warning("Skipping message from unsupported Kafka topic: {}", topic)
        return None

    if not value or not value.strip():
        return None

    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning("Skipping non-UTF-8 Kafka message on topic {}", topic)
        return None

    return _parse_alert_payload(text)
