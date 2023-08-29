# cart/models.py

# Codigo para modelo de carrinho de compras
from django.http import JsonResponse
from produtos.models import Produto, Variation, Category
from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone
import logging

# Configuração inicial para logs
logger = logging.getLogger(__name__)


class Cupom(models.Model):
    STATUS_CHOICES = (
        ('Ativo', 'Ativo'),
        ('Inativo', 'Inativo'),
        ('Expirado', 'Expirado'),
        ('Utilizado', 'Utilizado'),
    )

    codigo = models.CharField(max_length=15, unique=True)
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    maximo_usos = models.IntegerField(default=1)
    usos_atuais = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Ativo')
    data_validade = models.DateTimeField(default=timezone.now)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_modificacao = models.DateTimeField(auto_now=True)
    estados_frete_gratis = models.CharField(max_length=100, blank=True, null=True, help_text="Estados para frete grátis, separados por vírgula")
    max_uso_por_cliente = models.PositiveIntegerField(default=None, null=True, blank=True, help_text="Máximo de uso por cliente. Deixe em branco ou coloque None para uso ilimitado.")
    tipo_de_frete_gratis = models.CharField(max_length=100, blank=True, null=True, help_text="Escolha o tipo de fretes que seram gratis, separados por vírgula")
    desconto_percentual_frete = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    desconto_fixo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimo_compra = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    produtos_aplicaveis = models.ManyToManyField(Produto, blank=True)
    categorias_aplicaveis = models.ManyToManyField(Category, blank=True)

    def __str__(self):
        return self.codigo

    def gerar_codigo(self):
        self.codigo = str(uuid.uuid4().hex.upper()[:15])

    def esta_ativo(self):
        return self.status == 'Ativo'

    def pode_ser_utilizado(self, total=None, produto=None, categoria=None, estado_entrega=None, tipo_frete=None, user= None):

        # Verifica status e validade
        if not self.esta_ativo():
            return False, "Cupom inativo ou expirado."
        if self.usos_atuais >= self.maximo_usos:
            return False, "Este cupom já foi totalmente utilizado."
        if timezone.now() > self.data_validade:
            return False, "Este cupom já expirou."

        # Verifica o limite mínimo de compra, se aplicável
        if total and not self.atende_limite_minimo(total):
            return False, "O valor total do pedido não atende ao mínimo necessário para usar este cupom."

        if self.max_uso_por_cliente:
            print("TESTEANDO USO MAX CLIENTE")
            from pedidos.models import Pedido

            usos_por_usuario = Pedido.objects.filter(user__email=user, cupom=self).count()
            print('usos_por_usuario:',usos_por_usuario)
            if usos_por_usuario >= self.max_uso_por_cliente:
                return False, 'Limite de uso do cupom atingido para este usuário.'

        # Verifica se o cupom é aplicável a um produto específico, se aplicável
        if produto and not self.aplicavel_a_produto(produto):
            return False, "Este cupom não é válido para o produto selecionado."

        # Verifica se o cupom é aplicável a uma categoria específica, se aplicável
        if categoria and not self.aplicavel_a_categoria(categoria):

            return False, "Este cupom não é válido para a categoria do produto selecionado."

        # Verifica se o cupom oferece frete grátis para o estado de entrega
        if estado_entrega and not self.aplicar_frete_gratis(estado_entrega):

            return False, "Este cupom não é válido para frete grátis no estado selecionado."

        # Verifica se o tipo de frete está entre os permitidos para frete grátis, se aplicável
        if tipo_frete and self.tipo_de_frete_gratis:
            tipos_permitidos = self.tipo_de_frete_gratis.split(',')
            if tipo_frete not in tipos_permitidos:
                return False, f"Este cupom só é válido para frete do tipo: {', '.join(tipos_permitidos)}."

        # Caso o usuário não tenha selecionado um tipo de frete, mas o cupom oferece frete grátis
        if self.tipo_de_frete_gratis and not tipo_frete:
            return False, "Por favor, selecione um tipo de frete para aplicar o cupom."

        return True, "Cupom aplicado com sucesso."

    def pode_ser_utilizado_finalizar_pedido(self, total=None, produto=None, categoria=None, estado_entrega=None, tipo_frete=None):
        """Verificacao para quando o cliente cliar em finalizar pedido para caso tenha mudado algo depois de aplicar o cupom"""
        # Verifica status e validade
        if not self.esta_ativo():
            return False, "Cupom inativo ou expirado."

        if timezone.now() > self.data_validade:
            return False, "Este cupom já expirou."

        # Verifica o limite mínimo de compra, se aplicável
        if total and not self.atende_limite_minimo(total):
            return False, "O valor total do pedido não atende ao mínimo necessário para usar este cupom."

        # Verifica se o cupom é aplicável a um produto específico, se aplicável
        if produto and not self.aplicavel_a_produto(produto):
            return False, "Este cupom não é válido para o produto selecionado."

        # Verifica se o cupom é aplicável a uma categoria específica, se aplicável
        if categoria and not self.aplicavel_a_categoria(categoria):

            return False, "Este cupom não é válido para a categoria do produto selecionado."

        # Verifica se o cupom oferece frete grátis para o estado de entrega
        if estado_entrega and not self.aplicar_frete_gratis(estado_entrega):

            return False, "Este cupom não é válido para frete grátis no estado selecionado."

        # Verifica se o tipo de frete está entre os permitidos para frete grátis, se aplicável
        if tipo_frete and self.tipo_de_frete_gratis:
            tipos_permitidos = self.tipo_de_frete_gratis.split(',')
            if tipo_frete not in tipos_permitidos:
                return False, f"Este cupom só é válido para frete do tipo: {', '.join(tipos_permitidos)}."

        # Caso o usuário não tenha selecionado um tipo de frete, mas o cupom oferece frete grátis
        if self.tipo_de_frete_gratis and not tipo_frete:
            return False, "Por favor, selecione um tipo de frete para aplicar o cupom."

        return True, "Cupom aplicado com sucesso."

    def adicionar_uso(self):
        self.usos_atuais += 1
        self.save()

    def aplicar_cupom(self, codigo_cupom):
        from pedidos.models import Pedido
        if not self.cupom:
            try:
                cupom = Cupom.objects.get(codigo=codigo_cupom)

                # Se max_uso_por_cliente não for None, verifique o uso
                if cupom.max_uso_por_cliente:
                    usos_por_usuario = Pedido.objects.filter(user=self.user, cupom=cupom).count()
                    if usos_por_usuario >= cupom.max_uso_por_cliente:
                        return False, 'Limite de uso do cupom atingido para este usuário.'

                if cupom.pode_ser_utilizado():
                    cupom.adicionar_uso()
                    self.cupom = cupom
                    self.save()
                    return True, 'Cupom aplicado com sucesso.'
                else:
                    return False, 'Cupom expirado ou limite de uso atingido.'
            except Cupom.DoesNotExist:
                return False, 'Cupom inválido.'
        else:
            return False, 'Já existe um cupom aplicado neste pedido.'

    def aplicar_frete_gratis(self, estado_entrega):

        if self:
            # Se estados_frete_gratis estiver vazio ou None, retorna True
            if not self.estados_frete_gratis:

                return True

            estados_frete_gratis = self.estados_frete_gratis.split(',')
            if estado_entrega in estados_frete_gratis:

                return True
        return False

    def aplicar_desconto(self, total):
        if self.desconto_percentual:
            valor_com_desconto = total * (1 - (self.desconto_percentual / 100))
            desconto = total - valor_com_desconto
            return desconto,valor_com_desconto
        elif self.desconto_fixo:
            valor_com_desconto = max(0, total - self.desconto_fixo)
            desconto = total - valor_com_desconto
            return desconto,valor_com_desconto
        return 0, total

    def aplicavel_a_produto(self, produto):
        if self.produtos_aplicaveis.exists():
            return produto in self.produtos_aplicaveis.all()
        return True

    def aplicavel_a_categoria(self, categoria):
        if self.categorias_aplicaveis.exists():
            return categoria in self.categorias_aplicaveis.all()
        return True

    def atende_limite_minimo(self, total):
        if self.minimo_compra:
            return total >= self.minimo_compra
        return True


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
                total += item.quantity * item.variation.preco_ou_valor_promocional
            else:
                total += item.quantity * item.product.preco_ou_valor_promocional
        return total

    def total_quantity(self):
        total = 0
        # Verifica se o carrinho tem itens
        if self.cartitem_set.exists():
            # Percorre todos os itens do carrinho
            for item in self.cartitem_set.all():
                total += item.quantity
        return total

    def add_item(self, product, quantity=1, variation=None):
        """
        Adiciona um produto ou variação ao carrinho.
        """
        try:
            # Verificar se o produto possui variações ou se uma variação específica foi fornecida
            if variation:
                # Verificar se a variação pertence ao produto
                if variation.produto_pai != product:
                    raise ValueError("A variação não pertence ao produto fornecido.")

                # Verificar o estoque da variação
                if not variation.tem_estoque_suficiente(quantity, self, self.user):
                    existing_items = CartItem.objects.filter(cart=self, variation__materia_prima=variation.materia_prima)
                    total_in_cart = sum(item.quantity * item.variation.gasto for item in existing_items)
                    raise ValueError(f"Estoque insuficiente para a variação {variation.name}. estoque disponivel {variation.materia_prima.stock} {variation.materia_prima.unidade}, {total_in_cart}{variation.materia_prima.unidade} ja estao no seu carrinho")

                # Adicionar ou atualizar o item do carrinho com a variação
                cart_item, created = CartItem.objects.get_or_create(cart=self, product=product, variation=variation)
            else:
                # Verificar o estoque do produto
                if not product.tem_estoque_suficiente(quantity, self, self.user):
                    existing_items = CartItem.objects.filter(cart=self, product__stock=product.stock)
                    total_in_cart = sum(item.quantity for item in existing_items)
                    print('Total in',total_in_cart)
                    pluralizar_unidade = "unidade" if product.stock == 1 else "unidades"

                    if total_in_cart:
                        raise ValueError(f"Estoque insuficiente para o produto {product.name}. estoque disponivel {product.stock} {pluralizar_unidade} e {total_in_cart}unidades ja estao no carrinho")
                    else:
                        raise ValueError(f"Estoque insuficiente para o produto {product.name}. estoque disponivel {product.stock} {pluralizar_unidade}.")

                # Adicionar ou atualizar o item do carrinho com o produto
                cart_item, created = CartItem.objects.get_or_create(cart=self, product=product)

            # Atualizar a quantidade do item do carrinho
            cart_item.quantity += quantity
            cart_item.save()

            return cart_item

        except Exception as e:
            logger.error(f"Erro ao adicionar item ao carrinho para o usuário {self.user.id}. Detalhes: {str(e)}")
            raise e

    def update_item(self, product_id, quantity, variation_id=None, fechamento=2):
        try:
            product = Produto.objects.get(id=product_id)
            variation = Variation.objects.get(id=variation_id) if variation_id else None
            quantity = int(quantity)
            if variation:
                if not variation.tem_estoque_suficiente(quantity, self, self.user, update=True):
                    raise ValueError(f"Estoque insuficiente para a variação {variation.name}. Temos {variation.materia_prima.stock} {variation.materia_prima.unidade} disponiveis")

                cart_item = CartItem.objects.get(cart=self, product=product, variation=variation)
            else:
                pluralizar_unidade = "unidade" if product.stock == 1 else "unidades"
                if not product.tem_estoque_suficiente(quantity, self, self.user, update=True):
                    raise ValueError(f"Estoque insuficiente para o produto {product.name}. Temos {product.stock} {pluralizar_unidade} disponiveis")

                cart_item = CartItem.objects.get(cart=self, product=product)

            cart_item.quantity = quantity
            cart_item.save()
            return True, 'Item atualizado com sucesso'

        except Produto.DoesNotExist:
            return False, 'Produto não encontrado'
        except Variation.DoesNotExist:
            return False, 'Variação não encontrada'
        except CartItem.DoesNotExist:
            return False, 'Item não encontrado no carrinho'
        except ValueError as e:
            return False, str(e)

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
            return self.quantity * self.variation.preco_ou_valor_promocional
        else:
            return self.quantity * self.product.preco_ou_valor_promocional

    # Representação em string do item no carrinho, no formato: quantidade x nome do produto no carrinho username do usuário
    def __str__(self):
        if self.variation:
            return f" {self.variation.name}"
        else:
            return f"{self.quantity} x {self.product.name} no carrinho {self.cart.user.username}"




