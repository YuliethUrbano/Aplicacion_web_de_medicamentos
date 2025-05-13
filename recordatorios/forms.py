from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
from django.forms import ModelForm
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['nombre_Medicamento', 'presentacion', 'frecuencia', 'important']
        widgets = {
            'nombre_Medicamento': forms.TextInput(attrs={'class': 'form-control'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            'frecuencia': forms.Select(attrs={'class': 'form-control'}),
            'important': forms.CheckboxInput(attrs={'class': 'form-check-input m-auto'}),
        }