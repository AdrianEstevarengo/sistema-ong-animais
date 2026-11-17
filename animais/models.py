from django.db import models


class Animal(models.Model):
    ESPECIES = [
        ('Cachorro', 'Cachorro'),
        ('Gato', 'Gato'),
    ]

    STATUS = [
        ('Disponível', 'Disponível'),
        ('Adotado', 'Adotado'),
        ('Em tratamento', 'Em tratamento'),
    ]

    nome = models.CharField(max_length=100)
    especie = models.CharField(max_length=20, choices=ESPECIES)
    raca = models.CharField(max_length=100, blank=True)
    idade = models.PositiveIntegerField(null=True, blank=True)
    sexo = models.CharField(max_length=10)
    porte = models.CharField(max_length=20)
    descricao = models.TextField(blank=True)
    status = models.CharField(
        max_length=30,
        choices=STATUS,
        default='Disponível'
    )
    foto = models.ImageField(
        upload_to='animais/',
        blank=True,
        null=True
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome


class Vacina(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='vacinas'
    )
    nome = models.CharField(max_length=100)
    data_aplicacao = models.DateField()
    proxima_dose = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.nome} - {self.animal.nome}'


class Anexo(models.Model):
    animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='anexos'
    )
    arquivo = models.FileField(upload_to='anexos/')
    descricao = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f'Anexo - {self.animal.nome}'