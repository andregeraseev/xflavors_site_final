# cart/models.py

# Codigo para modelo de carrinho de compras
from django.http import JsonResponse

from produtos.models import Produto, Variation
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone


class Cupom(models.Model):
    STATUS_CHOICES = (
        ('Ativo', 'Ativo'),
        ('Expirado', 'Expirado'),
        ('Utilizado', 'Utilizado'),
    )

    codigo = models.CharField(max_length=15, unique=True)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2)
    maximo_usos = models.IntegerField(default=1)
    usos_atuais = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Ativo')
    data_validade = models.DateTimeField(default=timezone.now)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.codigo

    def gerar_codigo(self):
        self.codigo = str(uuid.uuid4().hex.upper()[:15])

    def esta_ativo(self):
        return self.status == 'Ativo'

    def pode_ser_utilizado(self):
        return self.esta_ativo() and self.usos_atuais < self.maximo_usos and timezone.now() < self.data_validade

    def adicionar_uso(self):
        self.usos_atuais += 1
        self.save()




# Classe Cart, que representa o carrinho de compras de um usuário
class Cart(models.Model):
    # Usuário associado ao carrinho
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Data de criação do carrinho
    created_at = models.DateTimeField(auto_now_add=True)
    # Data da última atualização do carrinho
    updated_at = models.DateTimeField(auto_now=True)
    # Produtos contidos no carrinho
    cart_items = models.ManyToManyField(Produto, through='CartItem')
    # variassoes contidos no carrinho
    # todo
    variations = models.ManyToManyField(Variation, related_name='carts', blank=True)
    # Método que retorna ou cria o carrinho de um determinado usuário
    cupom = models.ForeignKey(Cupom, on_delete=models.SET_NULL, null=True, blank=True)

    # métodos do modelo

    def aplicar_cupom(self, codigo_cupom):
        if not self.cupom:
            try:
                cupom = Cupom.objects.get(codigo=codigo_cupom)
                self.cupom = cupom
            except Cupom.DoesNotExist:
                return False, 'Cupom inválido.'
            if self.cupom.pode_ser_utilizado():
                self.cupom.adicionar_uso()
                self.cupom = cupom
                self.save()
                return True, 'Cupom aplicado com sucesso.'
            else:
                return False, 'Cupom expirado.'
        else:
            return False, 'Já existe um cupom aplicado neste pedido.'



    @classmethod
    def get_or_create_cart(cls, user):
        # Verifica se o usuário não é anônimo
        if not user.is_anonymous:
            # Tenta obter o carrinho do usuário
            cart, created = Cart.objects.get_or_create(user=user)
            return cart
        return None

    # Método que adiciona um item ao carrinho
    @classmethod
    def add_item_to_cart(cls, cart, product,  quantity):
        # Tenta obter o item do carrinho ou o cria
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        # Adiciona a quantidade ao item
        cart_item.quantity += int(quantity)
        # Salva o item
        cart_item.save()

    # Método que retorna o número total de itens no carrinho
    def total_items(self):
        total = 0
        # Percorre todos os itens do carrinho
        for item in self.cartitem_set.all():
            total += item.quantity
        return total



    def remove_item(request, product_id):
        cart = Cart.objects.get_or_create_cart(request.user)
        if cart:
            try:
                item = CartItem.objects.get(cart=cart, product__id=product_id)
                item.delete()
                return JsonResponse({'status': 'success'})
            except CartItem.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Item não encontrado no carrinho'})
        return JsonResponse({'status': 'error', 'message': 'Carrinho não encontrado'})

    # Método que limpa o carrinho
    def clear_cart(cls, cart):
        # Deleta todos os itens do carrinho
        cart.cartitem_set.all().delete()

    # Método que retorna o preço total do carrinho
    def total_price(self):
        total = 0
        # Percorre todos os itens de carrinho
        for item in self.cartitem_set.all():
            if item.variation:
                total += item.quantity * item.variation.price
            else:
                total += item.quantity * item.product.price
        return total

    def total_quantity(self):
        total = 0
        # Verifica se o carrinho tem itens
        if self.cartitem_set.exists():
            # Percorre todos os itens do carrinho
            for item in self.cartitem_set.all():
                total += item.quantity
        return total


    # Método que retorna a representação em string do carrinho
    def __str__(self):
        return f"Carrinho do usuário {self.user.username}"


# Classe CartItem, que representa um item no carrinho
class CartItem(models.Model):
    # Carrinho ao qual o item está associado
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # Relacionamento com a classe Produto, representando o produto adicionado ao carrinho
    product = models.ForeignKey(Produto, on_delete=models.CASCADE)
    # Quantidade do produto adicionado ao carrinho
    quantity = models.PositiveIntegerField(default=0)
    # Método para calcular o preço total do item, multiplicando a quantidade pelo preço unitário do produto
    variation = models.ForeignKey(Variation, on_delete=models.SET_NULL, null=True)
    # Relacionamento com a classe Variation, representando a variacao adicionado ao carrinho

    def total_price(self):
        if self.variation:
            return self.quantity * self.variation.price
        else:
            return self.quantity * self.product.price

    # Representação em string do item no carrinho, no formato: quantidade x nome do produto no carrinho username do usuário
    def __str__(self):
        if self.variation:
            return f" {self.variation.name}"
        else:
            return f"{self.quantity} x {self.product.name} no carrinho {self.cart.user.username}"




