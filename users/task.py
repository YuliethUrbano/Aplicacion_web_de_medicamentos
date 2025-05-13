# recordatorios/tasks.py
from celery import shared_task
from django.utils import timezone
from .models import Toma

@shared_task
def actualizar_estados_tomas():
    hora_actual = timezone.now()
    Toma.objects.filter(
        estado="pendiente",
        hora__lt=hora_actual
    ).update(estado="omitida")