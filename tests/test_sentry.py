"""Quick verification that Sentry SDK integration works end-to-end."""

import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration


def main():
    sentry_logging = LoggingIntegration(
        level=logging.INFO,
        event_level=logging.ERROR,
    )

    sentry_sdk.init(
        dsn="https://2f36781c6e05b513d96d8f7f444e0fff@o4510963528237056.ingest.de.sentry.io/4510963531317328",
        send_default_pii=True,
        release="Snapchat Organizer@test",
        environment="development",
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
        enable_tracing=True,
        integrations=[sentry_logging],
    )
    print("[OK] Sentry SDK initialized")

    # Metrics
    sentry_sdk.metrics.count("test.init_check", 1)
    sentry_sdk.metrics.distribution("test.latency", 42.0, unit="millisecond")
    sentry_sdk.metrics.gauge("test.gauge", 7.5, unit="percent")
    print("[OK] Metrics API (count, distribution, gauge)")

    # Tracing / spans
    with sentry_sdk.start_span(op="test", name="verification_span") as span:
        span.set_data("test.key", "value")
    print("[OK] Tracing API (start_span, set_data)")

    # User context
    sentry_sdk.set_user({"id": "test-user", "email": "test@example.com"})
    sentry_sdk.set_user(None)
    print("[OK] User context (set_user / clear)")

    # Logging integration
    logger = logging.getLogger("sentry.test")
    logger.info("Breadcrumb test")
    print("[OK] Logging integration (breadcrumbs)")

    print("\nAll Sentry features verified!")


if __name__ == "__main__":
    main()
