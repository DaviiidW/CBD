import time
from django.core.management.base import BaseCommand
from apps.graph.services import recommendation_service

class Command(BaseCommand):
    help = 'Recalcula las similitudes de usuarios usando Neo4j Graph Data Science (GDS)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('[!] Iniciando proceso de recomendación Neo4j GDS...'))
        start_time = time.time()
        
        try:
            stats = recommendation_service.recompute_all()
            duration = time.time() - start_time
            
            self.stdout.write(self.style.SUCCESS(f'[OK] Similitudes recalculadas con éxito en {duration:.2f} segundos.'))
            
            if stats:
                try:
                    self.stdout.write(self.style.SUCCESS(f"Detalles GDS: {stats}"))
                except Exception:
                    pass
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'[ERROR] Falló el recálculo GDS: {str(e)}'))
            self.stdout.write(self.style.WARNING(
                'Nota: Asegúrate de tener Neo4j iniciado y con el plugin Graph Data Science (GDS) instalado y habilitado.'
            ))
