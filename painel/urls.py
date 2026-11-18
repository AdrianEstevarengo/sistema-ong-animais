from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('avisos/', views.avisos, name='avisos'),
    path('atendimentos/', views.atendimento_lista, name='atendimento_lista'),
    path('atendimentos/novo/', views.atendimento_form, name='atendimento_novo'),
    path('atendimentos/<int:pk>/editar/', views.atendimento_form, name='atendimento_editar'),
    path('atendimentos/<int:pk>/excluir/', views.atendimento_excluir, name='atendimento_excluir'),
]
