"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from recordatorios import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name= 'home'),
    path('signup/', views.signup, name='signup'),
    path('medicamentos/', views.medicamentos, name='medicamentos'),
    path('medicamentos_completed/', views.medicamentos_completed, name='medicamentos_completed'),
    path('actualizar_tomas/', views.actualizar_tomas, name='actualizar_tomas'),
    path('historial/', views.historial, name='historial'),
    path('noti/', views.noti, name='noti'),
    path("notificaciones/", views.obtener_notificaciones, name="obtener_notificaciones"),
    path('noti/confirmar/<int:notificacion_id>/', views.confirmar_toma, name='confirmar_toma'),
    path('noti/retrasar/<int:notificacion_id>/', views.retrasar_toma, name='retrasar_toma'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('tasks/<int:task_id>/complete/', views.complete_task, name='complete_task'),
    path('tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('logout/', views.signout, name='logout'),
    path('signin/', views.signin, name='signin'),
    path('homelogin/', views.homelogin, name='homelogin'),
    path('marcar_toma/<int:toma_id>/', views.marcar_toma, name='marcar_toma')
    
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
