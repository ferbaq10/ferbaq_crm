import os
from decouple import config
import dj_database_url

# --- SECRET KEY ---
SECRET_KEY = os.environ.get("SECRET_KEY") or config("SECRET_KEY", default="insecure-default")

# --- DEBUG ---
DEBUG = config("DEBUG", default=True, cast=bool)

# --- DATABASE ---
DATABASE_URL = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default=None)
print(f"🔍 DATABASE_URL desde entorno: {DATABASE_URL}")
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    print(f"🔍 DATABASE: {config('DB_NAME', default='ferbaq_local')}")
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='ferbaq_local'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='password'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432', cast=int),
        }
    }

# --- REDIS ---
REDIS_URL = os.environ.get('REDIS_URL')
if not REDIS_URL:
    REDIS_URL = f"redis://{config('REDIS_HOST', default='127.0.0.1')}:{config('REDIS_PORT', default='6379')}/{config('REDIS_DB', default='1')}"

try:
    import redis
    r = redis.from_url(REDIS_URL)
    r.ping()

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "SERIALIZER": "django_redis.serializers.json.JSONSerializer",
            }
        }
    }
    print("✅ Usando Redis para cache")
except Exception:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }
    print("⚠️ Redis no disponible, cache deshabilitado. Todas las consultas irán a la base de datos.")

RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DEFAULT_TIMEOUT': 360,
    }
}

ROOT_URLCONF = 'core.urls'
