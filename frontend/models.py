from django.db import models

from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

class Banner(models.Model):
    """
    Model de Banner
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='banners')
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para criar o slug a partir do nome.
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def image_url(self):
        """
        Retorna a URL da imagem do banner.
        """
        return self.image.url

    def is_active(self):
        """
        Retorna True se o banner está ativo e dentro do intervalo de datas programado.
        """
        if not self.active:
            return False
        now = timezone.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    def __str__(self):
        """
        Retorna a representação em string do banner.
        """
        return self.name

    # def save(self, *args, **kwargs):
    #     # Sobrescreve o método save para criar o slug a partir do nome.
    #     self.slug = slugify(self.name)
    #
    #     # Redimensiona a imagem para 800x600 pixels.
    #     super().save(*args, **kwargs)
    #     image = Image.open(self.image.path)
    #     image = image.resize((1200, 800))
    #     image.save(self.image.path)

class BannerMenor(models.Model):
    """
    Model de Banner
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='banners')
    active = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para criar o slug a partir do nome.
        """
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def image_url(self):
        """
        Retorna a URL da imagem do banner.
        """
        return self.image.url

    def is_active(self):
        """
        Retorna True se o banner está ativo e dentro do intervalo de datas programado.
        """
        if not self.active:
            return False
        now = timezone.now()
        if self.start_date and self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True

    def __str__(self):
        """
        Retorna a representação em string do banner.
        """
        return self.name