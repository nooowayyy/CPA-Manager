from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from cpa.defaults import DEFAULT_PLATFORMS, DEFAULT_CHANNELS
from cpa.models import Platform, Channel


class Command(BaseCommand):
    help = "Cria plataformas e canais padrão do CPA Manager para usuários existentes."

    def handle(self, *args, **options):
        users = get_user_model().objects.all().iterator()
        count = 0
        for user in users:
            for code, name in DEFAULT_PLATFORMS:
                Platform.objects.get_or_create(user=user, code=code, defaults={"name": name})
            for code, name in DEFAULT_CHANNELS:
                Channel.objects.get_or_create(user=user, code=code, defaults={"name": name})
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Dimensões padrão verificadas para {count} usuário(s)."))
