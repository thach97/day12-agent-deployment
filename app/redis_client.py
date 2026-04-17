import redis as redis_lib

from config import settings

# ssl_cert_reqs=None required for Upstash (and other managed Redis with TLS)
redis = redis_lib.from_url(settings.REDIS_URL, decode_responses=True, ssl_cert_reqs=None)
