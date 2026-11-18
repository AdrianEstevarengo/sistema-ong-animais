from django.contrib import admin
from .models import Atendimento


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = ('data', 'tipo', 'nome_animal', 'especie', 'responsavel', 'situacao', 'custo')
    list_filter = ('tipo', 'situacao')
    search_fields = ('nome_animal', 'responsavel', 'local', 'descricao')
