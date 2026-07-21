import os  # noqa: F401
from task_manager.settings.base import *  #  noqa: F403 F405

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = []

RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")  # noqa: F403 F405

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",  # noqa: F405
        "NAME": os.environ["POSTGRES_DB"],  # noqa: F405
        "USER": os.environ["POSTGRES_USER"],  # noqa: F405
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],  # noqa: F405
        "HOST": os.environ["POSTGRES_HOST"],  # noqa: F405
        "PORT": int(os.environ["POSTGRES_DB_PORT"]),  # noqa: F405
    }
}
