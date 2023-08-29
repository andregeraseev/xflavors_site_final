# produtos/models.py
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify
from clientes.models import Cliente
import logging

# Configuração inicial para logs
logger = logging.getLogger(__name__)


class Category(models.Model):
    """
    Model de categoria de produtos
    """
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
class Subcategory(models.Model):
    """
    Model de subcategoria de produtos
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('produtos:produto_por_subcategoria', args=[str(self.category.id), str(self.id)])



class MateriaPrima(models.Model):
    """
    Model de variação de produtos
    """
    name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField()
    unidade = models.CharField(max_length=100, default='mls')
    id_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)
    sku_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name





class Produto(models.Model):
    """
    Model de produto
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    stock = models.PositiveIntegerField( blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, default=0.04)
    marca = models.CharField(max_length=50, blank=True, null=True)
    localizacao = models.CharField(max_length=100, blank=True, null=True, default="Sem localizacao")
    num_vendas = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promocao_ativa = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    id_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)
    sku_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)
    def save(self, *args, **kwargs):
        """
        Sobrescreve o método de salvar para atribuir o valor ao campo slug
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_category(self):
        """
        Retorna a categoria do produto
        """
        return self.category

    def __str__(self):
        """
        Retorna o nome do produto
        """
        return self.name

    def get_absolute_url(self):
        """
        Retorna a URL para acessar este produto
        """
        return reverse('product_detail', args=[str(self.slug)])
    @property
    def get_stock(self):
        if self.variation_set.exists():
            variation = self.variation_set.first()
            if variation.materia_prima:
                return variation.materia_prima.stock
            else:
                return variation.stock
        else:
            return self.stock

    def tem_estoque_suficiente(self, quantity, cart, user, update=False):
        from cart.models import CartItem

        # Verifique se o carrinho pertence ao usuário
        if cart.user != user:
            logger.warning(f"Usuário {user} tentou acessar o carrinho de outro usuário {cart.user}")
            raise ValueError("O carrinho não pertence ao usuário atual.")

        try:
            existing_items = CartItem.objects.filter(cart=cart, product=self)
            total_in_cart = sum(item.quantity for item in existing_items)
            if update == True:
                total_in_cart = 0
            if quantity + total_in_cart  > self.stock:
                logger.info(f"Estoque insuficiente para o produto {self} com id{self.id} para o usuário {user}")
                return False
            return True

        except Exception as e:
            logger.error(
                f"Erro ao verificar o estoque do produto {self} com id{self.id} para o usuário {user}. Detalhes: {str(e)}")
            raise e

    @property
    def verifica_promocao(self):
        if self.preco_promocional and self.promocao_ativa == True:
            return True
        else:
            return False

    @property
    def preco_ou_valor_promocional(self):
        if self.preco_promocional and self.promocao_ativa == True:
            return self.preco_promocional
        else:
            return self.price

class Favorito(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    produto = models.ManyToManyField(Produto)


class Variation(models.Model):
    """
    Model de variação de produtos
    """
    name = models.CharField(max_length=100)
    nome_simplificado = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.PositiveIntegerField( blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2,default=0.04)
    produto_pai = models.ForeignKey(Produto,on_delete=models.CASCADE, blank=True, null=True)
    materia_prima = models.ForeignKey(MateriaPrima,on_delete=models.CASCADE, blank=True, null=True)
    gasto = models.PositiveIntegerField(default=1)
    unidade= models.CharField(max_length=100, default='unidade')
    num_vendas = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    preco_promocional = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    promocao_ativa = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    id_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)
    sku_mapeamento_tiny = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.name

    @property
    def verifica_promocao(self):
        if self.preco_promocional and self.promocao_ativa == True:
            return True
        else:
            return False
    @property
    def preco_ou_valor_promocional(self):
        if self.preco_promocional and self.promocao_ativa == True:
            return self.preco_promocional
        else:
            return self.price

    def tem_estoque_suficiente(self, quantity, cart, user, update=False):
        from cart.models import CartItem

        # Verifique se o carrinho pertence ao usuário
        if cart.user != user:
            logger.warning(f"Usuário {user} tentou acessar o carrinho de outro usuário {cart.user}")
            raise ValueError("O carrinho não pertence ao usuário atual.")

        try:
            total_required = quantity * self.gasto
            existing_items = CartItem.objects.filter(cart=cart, variation__materia_prima=self.materia_prima)
            total_in_cart = sum(item.quantity * item.variation.gasto for item in existing_items)
            print("TPADADE",update)
            if update == True:
                total_in_cart -= (cart.cartitem_set.get(variation=self).quantity) * self.gasto

            if total_required + total_in_cart > self.materia_prima.stock:
                print("TOTAL2", total_in_cart)
                print(total_required)
                logger.info(f"Estoque insuficiente para a variação {self} com id{self.id} para o usuário {user}")
                return False
            return True

        except Exception as e:
            logger.error(
                f"Erro ao verificar o estoque da variação {self} com id{self.id} para o usuário {user}. Detalhes: {str(e)}")
            raise e


class Kit(models.Model):
    """
    Model de kit de produtos
    """
    name = models.CharField(max_length=255)
    resumo = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='kits')
    variacoes = models.ManyToManyField(Variation)
    num_vendas = models.IntegerField(default=0)
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método de salvar para atribuir o valor ao campo slug
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def info_estoque(self):
        total_variacoes = self.variacoes.count()
        variacoes_disponiveis = self.variacoes.filter(materia_prima__stock__gte=10).count()
        if total_variacoes == variacoes_disponiveis:
            return "Todas essências disponíveis"
        else:
            return f"Temos {variacoes_disponiveis} essencias disponiveis de {total_variacoes}"

    def __str__(self):
        return self.name


