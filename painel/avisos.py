"""Regras dos avisos de vacinas/vermífugos/antiparasitários.

Usa o model Vacina do app animais (campo proxima_dose). Um aviso é:
- atrasado: proxima_dose já passou;
- perto de vencer: proxima_dose entre hoje e hoje + DIAS_ANTECEDENCIA.
Animais adotados (ou falecidos, se o status existir) não geram aviso.
"""
from datetime import timedelta

from django.utils import timezone

from animais.models import Vacina

DIAS_ANTECEDENCIA = 7
STATUS_SEM_AVISO = ['Adotado', 'Falecido']


def calcular_avisos(dias=DIAS_ANTECEDENCIA):
    hoje = timezone.localdate()
    limite = hoje + timedelta(days=dias)

    base = (
        Vacina.objects
        .select_related('animal')
        .filter(proxima_dose__isnull=False, proxima_dose__lte=limite)
        .exclude(animal__status__in=STATUS_SEM_AVISO)
        .order_by('proxima_dose')
    )

    # Se a mesma dose já foi reaplicada depois (registro novo com mesmo nome),
    # o aviso antigo não deve aparecer.
    atrasados, proximos = [], []
    for v in base:
        reaplicada = Vacina.objects.filter(
            animal=v.animal, nome__iexact=v.nome,
            data_aplicacao__gt=v.data_aplicacao,
        ).exists()
        if reaplicada:
            continue
        v.dias = (v.proxima_dose - hoje).days
        v.atraso = -v.dias
        (atrasados if v.dias < 0 else proximos).append(v)

    return {
        'hoje': hoje,
        'dias': dias,
        'atrasados': atrasados,
        'proximos': proximos,
    }
