from django.shortcuts import render, get_object_or_404, redirect
from django.utils.timezone import now, localtime, timedelta
import datetime
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from django.contrib import messages
from .forms import TaskForm
from .models import UserProfile
from .models import Task
from .models import Toma
from .models import HistorialToma
from .models import Notificacion
from django.contrib.auth.decorators import login_required

def actualizar_tomas(request):
    if not request.user.is_authenticated:
        return JsonResponse({}, status=403)

    hora_actual = timezone.localtime(timezone.now())
    
    # Actualizar tomas omitidas
    Toma.objects.filter(estado="pendiente", hora__lt=hora_actual).update(estado="omitida")

    # Obtener las tomas pendientes actualizadas
    tomas_pendientes = Toma.objects.filter(
        estado="pendiente",
        medicamento__user=request.user,
        hora__gte=hora_actual
    ).order_by('hora')[:4]

    return render(request, 'partials/tomas_pendientes.html', {
        'tomas_pendientes': tomas_pendientes
    })

# Create your views here.
def home(request):
    if request.user.is_authenticated:
        return render(request, 'homelogin.html')
    return render(request, 'home.html')

def homelogin(request):
    if not request.user.is_authenticated:
        return redirect('home')

    hora_actual = timezone.localtime(timezone.now())
    hora_actual_time = hora_actual.time()

    # Marcar como "omitidas" las tomas que ya pasaron
    Toma.objects.filter(
        estado="pendiente", 
        hora__lt=hora_actual_time
    ).update(estado="omitida")

    # Obtener las 4 tomas más cercanas a la hora actual
    tomas_pendientes = Toma.objects.filter(
        estado="pendiente",
        medicamento__user=request.user,
        hora__gte=hora_actual_time
    ).order_by('hora')[:4]  

    # Obtener las tomas omitidas
    tomas_omitidas = Toma.objects.filter(
        estado="omitida", 
        medicamento__user=request.user
    ).order_by('-hora')

    return render(request, 'homelogin.html', {
        'tomas_pendientes': tomas_pendientes,
        'tomas_omitidas': tomas_omitidas
    })


def marcar_toma(request, toma_id):
    toma = get_object_or_404(Toma, id=toma_id)

    if toma.estado != "tomada":
        toma.estado = "tomada"
        toma.save()
        hora_actual = now()
        
        HistorialToma.objects.create(
            fecha=hora_actual.date(),
            hora_real=hora_actual.time(),
            estado="tomada",
            toma=toma
        )
        messages.success(request, "La toma ha sido marcada como tomada.")
    else:
        messages.warning(request, "Esta toma ya estaba marcada como tomada.")

    return redirect('homelogin')

@login_required(login_url='signin')
def historial(request):
    historial = HistorialToma.objects.filter(
        toma__medicamento__user=request.user,
        estado="tomada"
    ).order_by("-fecha", "-hora_real")

    return render(request, 'historial.html', {'historial': historial})

@login_required(login_url='signin')
def noti(request):
    hora_actual = timezone.localtime(timezone.now())  
    ahora = hora_actual.time()  

    tomas_pendientes = Toma.objects.filter(Q(estado="pendiente") | Q(estado="omitida"), hora__lte=ahora)

    for toma in tomas_pendientes:
        user = toma.medicamento.user  
        if not Notificacion.objects.filter(toma=toma).exists():
            Notificacion.objects.create(
                usuario=user,
                toma=toma,
                hora_programada=toma.hora,
            )
    # Obtener todas las notificaciones para mostrarlas en la página
    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by('-hora_programada')
    return render(request, 'noti.html', {'notificaciones': notificaciones})
    
def confirmar_toma(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)

    notificacion.toma.estado = "tomada"
    notificacion.toma.save()
    notificacion.delete()

    messages.success(request, "La toma ha sido confirmada exitosamente.")
    return redirect('noti')

def obtener_notificaciones(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(usuario=request.user)
        data = [
            {"id": n.id, "mensaje": f"Toma tu medicamento: {n.toma.medicamento.nombre_Medicamento} a las {n.hora_programada}"}
            for n in notificaciones
        ]
        return JsonResponse({"notificaciones": data})
    return JsonResponse({"error": "Usuario no autenticado"}, status=401)

def retrasar_toma(request, notificacion_id):
    """Retrasa la toma 30 minutos."""
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)

    nueva_hora = (datetime.combine(date.today(), notificacion.toma.hora) + timedelta(minutes=30)).time()
    notificacion.toma.hora = nueva_hora
    notificacion.toma.save()
    notificacion.hora_programada = nueva_hora
    notificacion.save()

    messages.info(request, "La toma ha sido retrasada 30 minutos.")
    return redirect('noti')


def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # Verificar si el correo ya existe
            if User.objects.filter(email=request.POST['email']).exists():
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El correo ya está en uso'
                })

            try:
                user = User.objects.create_user(
                    username=request.POST['username'],
                    first_name=request.POST['first_name'],
                    last_name=request.POST['last_name'],
                    email=request.POST['email'],
                    password=request.POST['password1']
                )
                user.save()
                
                # Guardar el rol del usuario
                role = request.POST.get('role', 'paciente')
                UserProfile.objects.create(user=user, role=role)
                
                login(request, user)
                return redirect('medicamentos')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El usuario ya existe'
                })
    
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las contraseñas no coinciden'
        })


def medicamentos(request):
    if not request.user.is_authenticated:
        return render(request, 'medicamentos.html', {'mensaje': 'Inicia sesión para ver tus medicamentos'})

    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'medicamentos.html', {'tasks': tasks})

@login_required(login_url='signin')
def medicamentos_completed(request):
    if not request.user.is_authenticated:
        return render(request, 'medicamentos.html', {'mensaje': 'Inicia sesión para ver tus medicamentos'})

    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'medicamentos.html', {'tasks': tasks})

@login_required(login_url='signin')
def create_task(request):
    if request.method == 'GET':
        return render(request, 'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            if form.is_valid():
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()

                # Obtener la hora de inicio desde el formulario
                hora_inicio_str = request.POST.get("hora_inicio")  # Formato string "HH:MM"
                if hora_inicio_str:
                    hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
                    crear_tomas(new_task, hora_inicio)  # Generar las tomas automáticas
                    
                # Agregar mensaje de éxito
                messages.success(request, f"El medicamento '{new_task.nombre_Medicamento}' ha sido creado exitosamente.")
                return redirect('medicamentos')
            else:
                return render(request, 'create_task.html', {
                    'form': TaskForm,
                    'error': 'Por favor ingrese datos válidos'
                })
        except ValueError:
            return render(request, 'create_task.html', {
                'form': TaskForm,
                'error': 'Error al procesar los datos'
            })

@login_required(login_url='signin')
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form' : form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('medicamentos')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form' : form, 'error' : "Error al actulizar medicamento"})

@login_required(login_url='signin')
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('medicamentos')

@login_required(login_url='signin')    
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('medicamentos')

def crear_tomas(medicamento, hora_inicio):
    frecuencia = medicamento.frecuencia
    tomas = []
    hora_actual = datetime.combine(now().date(), hora_inicio)

    for i in range(24 // frecuencia):  # Calcular las tomas del día
        tomas.append(Toma(medicamento=medicamento, hora=hora_actual.time()))
        hora_actual += timedelta(hours=frecuencia)

    Toma.objects.bulk_create(tomas)
        
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method =='GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {
            'form': AuthenticationForm,
            'error': 'El usuario o la contraseña es incorrecto'
        })
        else:
            login(request, user)
            return redirect('medicamentos')