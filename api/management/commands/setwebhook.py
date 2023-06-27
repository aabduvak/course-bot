from django.core.management.base import BaseCommand
from django.conf import settings
import requests

class Command(BaseCommand):
    help = 'Starts the Telegram bot'

    def handle(self, *args, **options):
        url = f'https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/setWebhook'
        webhook_url = f'https://{settings.ALLOWED_HOSTS[0]}/webhook/'
        response = requests.get(url, params={'url': webhook_url})