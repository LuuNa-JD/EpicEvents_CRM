import sentry_sdk
import os
from dotenv import load_dotenv

load_dotenv()

SENTRY_DSN = os.getenv("SENTRY_DSN")

if not SENTRY_DSN:
    print("❌ SENTRY_DSN non défini. Sentry ne sera pas activé.")

else:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        send_default_pii=True,
        traces_sample_rate=1.0
        )
    print("✅ Sentry est activé.")
