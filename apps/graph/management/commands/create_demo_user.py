from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

DEMO_USERNAME = 'demo'
DEMO_PASSWORD = 'demo1234'
DEMO_EMAIL = 'demo@techgraph.local'


class Command(BaseCommand):
    help = 'Crea el usuario de demostración (demo / demo1234) si no existe.'

    def handle(self, *args, **options):
        if User.objects.filter(username=DEMO_USERNAME).exists():
            self.stdout.write(self.style.WARNING(
                f'El usuario "{DEMO_USERNAME}" ya existe. No se ha modificado.'
            ))
            return

        User.objects.create_user(
            username=DEMO_USERNAME,
            email=DEMO_EMAIL,
            password=DEMO_PASSWORD,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Usuario de demo creado:\n'
            f'  Usuario:    {DEMO_USERNAME}\n'
            f'  Contraseña: {DEMO_PASSWORD}\n'
            f'  (Solo para desarrollo. No usar en producción.)'
        ))
