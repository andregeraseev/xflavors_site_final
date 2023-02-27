# produtos/models.py
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify

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






class Produto(models.Model):
    """
    Model de produto
    """
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    stock = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, blank=True, null=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, default=0.04)
    marca = models.CharField(max_length=50, blank=True, null=True)
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

class Variation(models.Model):
    """
    Model de variação de produtos
    """
    name = models.CharField(max_length=100)
    nome_simplificado = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    peso = models.DecimalField(max_digits=10, decimal_places=2,default=0.04)
    produto_pai = models.ForeignKey(Produto,on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name