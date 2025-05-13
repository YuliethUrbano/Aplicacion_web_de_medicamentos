from django.db import models
from django.contrib.auth.models import User

# Modelo para almacenar roles de usuario
class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('paciente', 'Paciente'),
        ('cuidador', 'Cuidador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='paciente')

    def __str__(self):
        return f"{self.user.username} - {self.role}"

 # Modelo de Relacion paciente cuidador
class RelacionCuidadorPaciente(models.Model):
    paciente = models.ForeignKey(User, on_delete=models.CASCADE, related_name="paciente")
    cuidador = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cuidador")

    def __str__(self):
        return f"Paciente: {self.paciente.username} - Cuidador: {self.cuidador.username}"

# Modelo de Tareas (Medicamentos)
class Task(models.Model):
    FRECUENCIA_CHOICES = [
        (6, "Cada 6 horas"),
        (8, "Cada 8 horas"),
        (12, "Cada 12 horas"),
        (24, "Cada 24 horas"),
    ]

    nombre_Medicamento = models.CharField(max_length=100)
    presentacion = models.CharField(max_length=100)
    frecuencia = models.IntegerField(choices=FRECUENCIA_CHOICES, default=8)  # Frecuencia en horas
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre_Medicamento

# Modelo de Tomas del Medicamento
class Toma(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('tomada', 'Tomada'),
        ('omitida', 'Omitida'),
    ]
    medicamento = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="tomas")
    hora = models.TimeField()  # Se calculará automáticamente salvo la primera toma
    dosis = models.IntegerField(default=1) 
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')

# Modelo de Historial de Tomas
class HistorialToma(models.Model):
    toma = models.ForeignKey(Toma, on_delete=models.CASCADE, related_name="historial")
    fecha = models.DateField(auto_now_add=True)
    hora_real = models.TimeField(null=True, blank=True)
    estado = models.CharField(
        max_length=10,
        choices=[('pendiente', 'Pendiente'), ('tomado', 'Tomado'), ('omitido', 'Omitido')],
        default='pendiente'
    )

    def __str__(self):
        return f"{self.toma.medicamento.nombre_Medicamento} - {self.fecha} - {self.estado}"

# Modelo de Notificaciones de Tomas
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    toma = models.ForeignKey(Toma, on_delete=models.CASCADE)
    hora_programada = models.TimeField()
    estado = models.CharField(
        max_length=10,
        choices=[('pendiente', 'Pendiente'), ('procesada', 'Procesada')],
        default='pendiente'
    )
    
    def __str__(self):
        return f"Notificación para {self.usuario.username} - {self.hora_programada} - {self.estado}"

