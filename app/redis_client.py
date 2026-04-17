import redis as redis_lib

from config import settings

# Upstash requires TLS but doesn't need cert verification
_url = settings.REDIS_URL
if _url.startswith("rediss://") and "ssl_cert_reqs" not in _url:
    _url += ("&" if "?" in _url else "?") + "ssl_cert_reqs=none"

redis = redis_lib.from_url(_url, decode_responses=True)
