# produtos/models.py
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify

from clientes.models import Cliente


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

    def __str__(self):
        return self.name


class Kit(models.Model):
    """
    Model de kit de produtos
    """
    name = models.CharField(max_length=255)
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


    def __str__(self):
        return self.name


