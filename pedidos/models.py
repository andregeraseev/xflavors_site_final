from clientes.models import EnderecoEntrega
from cart.models import Cart, Cupom
from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from clientes.models import EnderecoEntrega
from produtos.models import Produto, Variation
from cart.models import CartItem
import uuid
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncMonth

class PedidoItem(models.Model):

    # Relacionamento com a classe Produto, representando o produto adicionado ao pedido
    product = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True)
    # Quantidade do produto adicionado ao pedido
    quantity = models.PositiveIntegerField(default=0)
    # Método para calcular o preço total do item, multiplicando a quantidade pelo preço unitário do produto
    variation = models.ForeignKey(Variation, on_delete=models.SET_NULL,null=True, blank=True)
    # Relacionamento com a classe Variation, representando a variacao adicionado ao pedido
    price = models.DecimalField(max_digits=10, decimal_places=2, default=100)
    def valor_total(self):
        if self.variation:
            return self.quantity * self.variation.price
        return self.quantity * self.product.price


    def atualizar_vendas(self):
        if self.product:
            self.product.num_vendas += self.quantity
            self.product.save()
        if self.variation:
            self.variation.num_vendas += self.quantity
            self.variation.save()

    def __str__(self):
        product_name = 'Nenhum produto' if self.product is None else self.product.name
        if self.variation:
            product_name += f' ({self.variation.name})'
        return f'{self.quantity} x {product_name} '


class EnderecoPedido(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    rua = models.CharField(max_length=100)
    numero = models.CharField(max_length=20)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=8)











# Model para o pedido
class Pedido(models.Model):
    STATUS_CHOICES = (
        ('Aguardando pagamento', 'Aguardando pagamento'),
        ('Em processamento', 'Em processamento'),
        ('Pago', 'Pago'),
        ('Enviado', 'Enviado'),
        ('Em trânsito', 'Em trânsito'),
        ('Entregue', 'Entregue'),
        ('Pendente', 'Pendente'),
        ('Autorizado', 'Autorizado'),
        ('Em análise', 'Em análise'),
        ('Em mediação', 'Em mediação'),
        ('Rejeitado', 'Rejeitado'),
        ('Reembolsado', 'Reembolsado'),
        ('Estorno', 'Estorno'),
        ('Cancelado', 'Cancelado'),
    )
    FRETE_CHOICES = (
        ('Sedex', 'Sedex'),
        ('PAC', 'PAC'),
                        )
    PAGAMENTO_CHOICES = (
        ('MercadoPago', 'MercadoPago'),
        ('Pix', 'Pix'),
        ('Deposito', 'Deposito'),
        ('Pagseguro', 'Pagseguro'),

    )
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    endereco_entrega = models.ForeignKey(EnderecoPedido, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aguardando pagamento')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    itens = models.ManyToManyField(PedidoItem, blank=True, default=1)
    frete = models.CharField(max_length=20, choices=FRETE_CHOICES, default='Frete nao selecionado')
    valor_frete =  models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_de_pagamento = models.CharField(max_length=20, choices=PAGAMENTO_CHOICES, default='Nao selecionado')
    comprovante = models.FileField(upload_to='comprovantes', blank=True, null=True)
    numero_pedido_tiny = models.IntegerField(blank=True, null=True)
    mercado_pago_id = models.IntegerField(blank=True, null=True)
    rastreamento = models.CharField(max_length=30, blank=True, null=True)
    producao = models.BooleanField(default=False)
    observacoes = models.TextField(blank=True, null=True) # campo de observacoes do cliente
    observacoes_internas = models.TextField(blank=True, null=True) # campo de observacoes internar
    link_mercado_pago = models.CharField(max_length=400, blank=True, null=True) # link para pagar via mercado pago
    cupom = models.ForeignKey(Cupom, on_delete=models.SET_NULL, null=True, blank=True)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    # métodos do modelo




    class Meta:
        ordering = ('-data_pedido',)

    def atualizar_status(self, novo_status):
        self.status = novo_status
        self.save()

    def mudar_producao(self):
        self.producao = not self.producao
        self.save()

    def adicionar_observacao(self, observacao):
        self.observacoes = observacao
        self.save()

    def adicionar_observacao_interna(self, observacao_interna):
        self.observacoes_internas = observacao_interna
        self.save()

    def salvar_link_mercado_pago(self, link_mercado_pago):
        self.link_mercado_pago = link_mercado_pago
        self.save()


    @classmethod
    def get_vendas_por_mes(cls, year, month):
        return cls.objects.filter(data_pedido__year=year, data_pedido__month=month).aggregate(
            total_vendas=Sum('total')).get('total_vendas', 0)


def __str__(self):
        return f"Pedido {self.id}"












class Order(models.Model):
  # Relação 1 para N com o modelo de usuário, onde um usuário pode ter vários pedidos
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  # Relação 1 para 1 com o modelo de carrinho, onde um pedido é baseado em um carrinho
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
  # Indica se o pedido foi finalizado ou não
  ordered = models.BooleanField(default=False)
  # Número de identificação do pedido
  order_number = models.CharField(max_length=32, null=True)
  # Data e hora do pedido
  date_ordered = models.DateTimeField(auto_now_add=True)
  # Relação 1 para 1 com o modelo de endereço de entrega, onde um pedido tem um endereço de entrega associado
  shipping_address = models.ForeignKey(EnderecoEntrega, related_name='shipping_address', on_delete=models.SET_NULL, blank=True, null=True)
  # Número de rastreamento do pedido
  tracking_number = models.CharField(max_length=50, blank=True)
  # Data e hora de criação do modelo
  created_at = models.DateTimeField(auto_now_add=True)
  # Data e hora da última atualização do modelo
  updated_at = models.DateTimeField(auto_now=True)

  # Retorna o preço total dos itens no carrinho associado a este pedido
  def total_price(self):
    return self.cart.total_price()

  # Representação em string do objeto Order
  def __str__(self):
    return f"Pedido do usuário {self.user.username}"













