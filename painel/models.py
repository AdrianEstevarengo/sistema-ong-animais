from django.db import models
from django.utils import timezone


class Atendimento(models.Model):
    """Atendimentos/ajudas: animais que a ONG ajudou sem acolher no abrigo."""

    TIPOS = [
        ('Castração', 'Castração'),
        ('Consulta/Tratamento', 'Consulta/Tratamento'),
        ('Cirurgia', 'Cirurgia'),
        ('Vacinação', 'Vacinação'),
        ('Doação de ração', 'Doação de ração'),
        ('Doação de medicamento', 'Doação de medicamento'),
        ('Resgate', 'Resgate'),
        ('Outro', 'Outro'),
    ]

    SITUACOES = [
        ('Em andamento', 'Em andamento'),
        ('Concluído', 'Concluído'),
    ]

    data = models.DateField('Data', default=timezone.localdate)
    tipo = models.CharField('Tipo de ajuda', max_length=30, choices=TIPOS)
    nome_animal = models.CharField('Nome do animal', max_length=100, blank=True)
    especie = models.CharField(
        'Espécie', max_length=50, blank=True,
        help_text='Ex.: cachorro, gato, coruja...'
    )
    responsavel = models.CharField(
        'Responsável/solicitante', max_length=120, blank=True,
        help_text='Quem pediu a ajuda ou é tutor do animal'
    )
    contato = models.CharField('Contato', max_length=60, blank=True)
    local = models.CharField('Local/bairro', max_length=120, blank=True)
    descricao = models.TextField('Descrição', blank=True)
    custo = models.DecimalField(
        'Custo (R$)', max_digits=10, decimal_places=2, null=True, blank=True
    )
    situacao = models.CharField(
        'Situação', max_length=20, choices=SITUACOES, default='Em andamento'
    )
    data_cadastro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data', '-id']
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'

    def __str__(self):
        alvo = self.nome_animal or self.especie or 'animal'
        return f'{self.tipo} - {alvo} ({self.data:%d/%m/%Y})'
