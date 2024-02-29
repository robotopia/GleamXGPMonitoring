import os

from daiquiri.core.celery import get_celery_app

# from dotenv import load_dotenv
# load_dotenv()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = get_celery_app()
