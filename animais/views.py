from django.shortcuts import render
from .models import Animal


def lista_animais(request):
    animais = Animal.objects.all()

    especie = request.GET.get('especie')
    status = request.GET.get('status')
    porte = request.GET.get('porte')

    if especie:
        animais = animais.filter(especie=especie)

    if status:
        animais = animais.filter(status=status)

    if porte:
        animais = animais.filter(porte=porte)

    return render(request, 'animais/lista.html', {
        'animais': animais
    })