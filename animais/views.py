
from django.shortcuts import render, get_object_or_404
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


def detalhe_animal(request, animal_id):
    animal = get_object_or_404(Animal, id=animal_id)

    return render(request, 'animais/detalhe.html', {
        'animal': animal
    })
