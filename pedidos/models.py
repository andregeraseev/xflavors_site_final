from clientes.models import EnderecoEntrega
from cart.models import Cart
from django.contrib.auth.models import User
from django.db import models
from django.db import models
from django.contrib.auth.models import User
from clientes.models import EnderecoEntrega
from produtos.models import Produto, Variation
from cart.models import CartItem


# Model para o pedido
class Pedido(models.Model):
    STATUS_CHOICES = (
        ('Aguardando pagamento', 'Aguardando pagamento'),
        ('Em processamento', 'Em processamento'),
        ('Em trânsito', 'Em trânsito'),
        ('Entregue', 'Entregue'),
        ('Cancelado', 'Cancelado'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endereco_entrega = models.ForeignKey(EnderecoEntrega, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Aguardando pagamento')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    itens = models.ManyToManyField(CartItem)

    class Meta:
        ordering = ('-data_pedido',)

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













