# djangocrud/celery.py
import os
from celery import Celery

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Aplicacion_web_de_medicamentos.settings')

# Crea la instancia de Celery
app = Celery('Aplicacion_web_de_medicamentos')

# Configura Celery usando las settings de Django (prefijo "CELERY_")
app.config_from_object('django.conf:settings', namespace='CELERY')

# Busca tareas automáticamente en todas las apps Django
app.autodiscover_tasks()