import os
from datetime import timedelta
from pathlib import Path
import platform
import dj_database_url
from decouple import config, Csv


# --- SECRET KEY ---
SECRET_KEY = os.environ.get("SECRET_KEY") or config("SECRET_KEY", default="insecure-default")

# --- DEBUG ---
DEBUG = config("DEBUG", default=True, cast=bool)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'djoser',
    'corsheaders',
    'django_filters',
    'django_extensions',
    'django_rq',
    'project',
    'catalog',
    'contact',
    'client',
    'objetive',
    'opportunity',
    'purchase',
    'activity_log',
    'users',
]

MIDDLEWARE = [
    'middleware.sql_debug.SQLDebugMiddleware', # Middleware para depuración de SQL
    'simple_history.middleware.HistoryRequestMiddleware', # Middleware para historial de cambios
    'corsheaders.middleware.CorsMiddleware', # Middleware de CORS
    'django.middleware.security.SecurityMiddleware', # Seguridad de Django
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # Middleware CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'middleware.cache_user_groups.CacheUserGroupsMiddleware', # precarga en memoria los grupos del usuario autenticado
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=12),  # Token de acceso dura 12 horas
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),   # Token de refresco dura 7 días
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

DJOSER = {
    'SERIALIZERS': {
        'token_obtain_pair': 'users.serializers.MyTokenObtainPairSerializer',
        'current_user': 'users.serializers.UserWithRolesSerializer'
    }
}

ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv()) # aplica a peticiones HTTP directas al servidor.

CSRF_TRUSTED_ORIGINS = ["https://crm.portal-ferbaq.net"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOW_CREDENTIALS = True

# Configuración adicional de CORS

cors_origins = config('CORS_ALLOWED_ORIGINS', default='')
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',')]

# Headers permitidos
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Métodos permitidos
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# --- DATABASE ---
# --- DATABASE ---
DATABASE_URL = os.environ.get("DATABASE_URL") or config("DATABASE_URL", default=None)
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
    # Agregar configuraciones adicionales a la conexión parseada
    DATABASES['default'].update({
        'CONN_MAX_AGE': 60,  # Mantener conexiones por 1 minuto
        'OPTIONS': {
            'connect_timeout': 60,  # 60 segundos para conectar
            'options': '-c statement_timeout=30000'  # 30 segundos por consulta
        }
    })
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='ferbaq_crm_dev'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='password'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432', cast=int),
            'CONN_MAX_AGE': 60,  # Reutilizar conexiones por 1 minuto
            'OPTIONS': {
                'connect_timeout': 60,  # Timeout para establecer conexión
                'options': '-c statement_timeout=30000 -c idle_in_transaction_session_timeout=30000'
            }
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

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es'

USE_I18N = True

TIME_ZONE = 'UTC'

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/api/static/'
STATIC_ROOT = '/var/www/ferbaq_crm_backend/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field


ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')
INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'unknown')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

BASE_DIR = Path(__file__).resolve().parent.parent

# Detectar si estamos en Windows o Linux
IS_WINDOWS = os.name == "nt"

# Definir carpeta de logs
# En Windows -> BASE_DIR/logs
# En Linux -> /var/log/ferbaq (pero si no existe, cae en BASE_DIR/logs)
default_log_dir = BASE_DIR / "logs"
linux_log_dir = Path("/var/log/django")

if IS_WINDOWS:
    LOG_DIR = default_log_dir
else:
    LOG_DIR = linux_log_dir if linux_log_dir.exists() else default_log_dir

# Crear carpeta de logs si no existe
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'detailed': {
            'format': f'[{{asctime}}] [{ENVIRONMENT}] [{INSTANCE_NAME}] {{levelname}} {{name}} - {{message}}',
            'style': '{',
        },
    },

    'handlers': {
        'console_detailed': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': str(LOG_DIR / 'django_extensions.log'),  # Ruta dinámica
             'maxBytes': 5*1024*1024,  # 5 MB Para que no crezca los logs indefinidamente
             'backupCount': 5,
             'formatter': 'detailed',
        },
    },

    'loggers': {
        'django_extensions': {
            'handlers': ['console_detailed', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console_detailed'],  # Solo consola
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_USE_SSL = config('EMAIL_USE_SSL', default=False, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')

DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=f'Ferbaq Opportunity Manager <{EMAIL_HOST_USER}>')

FRONTEND_URL = config('FRONTEND_URL', default='')

# Agregar carpeta de templates para emails (dentro de users)
TEMPLATES[0]['DIRS'].append(BASE_DIR / 'users' / 'templates')