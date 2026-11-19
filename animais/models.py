
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone


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


class Adotante(models.Model):
    nome = models.CharField(max_length=150)
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    observacoes = models.TextField(blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Adotante'
        verbose_name_plural = 'Adotantes'
        ordering = ['nome']

    def __str__(self):
        return self.nome


class SolicitacaoAdocao(models.Model):
    STATUS_SOLICITACAO = [
        ('Pendente', 'Pendente'),
        ('Aprovada', 'Aprovada'),
        ('Recusada', 'Recusada'),
        ('Cancelada', 'Cancelada'),
    ]

    animal = models.ForeignKey(
        Animal,
        on_delete=models.PROTECT,
        related_name='solicitacoes_adocao'
    )

    adotante = models.ForeignKey(
        Adotante,
        on_delete=models.PROTECT,
        related_name='solicitacoes_adocao'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_SOLICITACAO,
        default='Pendente'
    )

    data_solicitacao = models.DateTimeField(auto_now_add=True)

    data_aprovacao = models.DateTimeField(
        null=True,
        blank=True
    )

    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Solicitação de adoção'
        verbose_name_plural = 'Solicitações de adoção'
        ordering = ['-data_solicitacao']

        constraints = [
            models.UniqueConstraint(
                fields=['animal'],
                condition=models.Q(status='Aprovada'),
                name='unica_adocao_aprovada_por_animal'
            )
        ]

    def clean(self):
        super().clean()

        if not self.animal_id:
            return

        animal = Animal.objects.get(pk=self.animal_id)

        if self.pk:
            anterior = SolicitacaoAdocao.objects.filter(
                pk=self.pk
            ).first()
        else:
            anterior = None

        # Não permite trocar o animal de uma adoção aprovada.
        if anterior and anterior.status == 'Aprovada':
            if anterior.animal_id != self.animal_id:
                raise ValidationError({
                    'animal': 'Não é permitido trocar o animal de uma adoção aprovada.'
                })

        # Uma aprovação existente pode ser editada sem
        # exigir que o animal volte a ficar disponível.
        mesma_aprovacao = (
            anterior is not None
            and anterior.status == 'Aprovada'
            and self.status == 'Aprovada'
            and anterior.animal_id == self.animal_id
        )

        if self.status == 'Aprovada' and not mesma_aprovacao:
            if animal.status != 'Disponível':
                raise ValidationError({
                    'animal': 'Este animal não está disponível para adoção.'
                })

        if self.status == 'Pendente' and animal.status != 'Disponível':
            if not (
                anterior
                and anterior.status == 'Pendente'
                and anterior.animal_id == self.animal_id
            ):
                raise ValidationError({
                    'animal': 'Este animal não está disponível para adoção.'
                })

        outra_aprovacao = SolicitacaoAdocao.objects.filter(
            animal_id=self.animal_id,
            status='Aprovada'
        )

        if self.pk:
            outra_aprovacao = outra_aprovacao.exclude(pk=self.pk)

        if self.status == 'Aprovada' and outra_aprovacao.exists():
            raise ValidationError({
                'animal': 'Este animal já possui uma adoção aprovada.'
            })

    def save(self, *args, **kwargs):
        with transaction.atomic():
            # Bloqueia o animal durante a operação nos
            # bancos que suportam SELECT FOR UPDATE.
            if self.animal_id:
                animal = Animal.objects.select_for_update().get(
                    pk=self.animal_id
                )
            else:
                animal = None

            anterior = None

            if self.pk:
                anterior = SolicitacaoAdocao.objects.filter(
                    pk=self.pk
                ).first()

            self.full_clean()

            aprovacao_nova = (
                self.status == 'Aprovada'
                and (
                    anterior is None
                    or anterior.status != 'Aprovada'
                )
            )

            if aprovacao_nova:
                self.data_aprovacao = timezone.now()

            elif self.status != 'Aprovada':
                self.data_aprovacao = None

            super().save(*args, **kwargs)

            if aprovacao_nova and animal:
                animal.status = 'Adotado'
                animal.save(update_fields=['status'])

    def __str__(self):
        return f'{self.adotante.nome} - {self.animal.nome}'
