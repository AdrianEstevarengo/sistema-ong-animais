
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_animais, name='lista_animais'),
    path('<int:animal_id>/', views.detalhe_animal, name='detalhe_animal'),
]
