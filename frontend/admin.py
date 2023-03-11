from django.contrib import admin
from django.utils.html import format_html
from django.forms import ClearableFileInput
from .models import Banner, BannerMenor


class ImagePreviewWidget(ClearableFileInput):
    """
    Widget que exibe uma miniatura da imagem selecionada.
    """
    template_name = 'admin/widgets/image_preview_widget.html'

    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js', 'admin/js/core.js')

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['image_url'] = value.url if value else ''
        return context


class BannerAdmin(admin.ModelAdmin):
    """
    Classe de administração para o model Banner.
    """
    list_display = ('name', 'image_preview', 'active', 'start_date', 'end_date')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'start_date'

    def image_preview(self, obj):
        """
        Retorna uma visualização da imagem do banner.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;">', obj.image.url)
        return '-'

    image_preview.short_description = 'Imagem'

    readonly_fields = ('active_image',)

    def active_image(self, obj):
        """
        Retorna uma tag HTML para exibir a imagem do banner escolhido.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;">', obj.image.url)
        return '-'

    active_image.short_description = 'Imagem Ativa'
    active_image.widget = ImagePreviewWidget


admin.site.register(Banner, BannerAdmin)


class ImagePreviewWidget_MENOR(ClearableFileInput):
    """
    Widget que exibe uma miniatura da imagem selecionada.
    """
    template_name = 'admin/widgets/image_preview_widget.html'

    class Media:
        css = {'all': ('admin/css/widgets.css',)}
        js = ('admin/js/vendor/jquery/jquery.js', 'admin/js/jquery.init.js', 'admin/js/core.js')

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['image_url'] = value.url if value else ''
        return context


class BannerMenorAdmin(admin.ModelAdmin):
    """
    Classe de administração para o model Banner.
    """
    list_display = ('name', 'image_preview', 'active', 'start_date', 'end_date')
    list_filter = ('active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    date_hierarchy = 'start_date'

    def image_preview(self, obj):
        """
        Retorna uma visualização da imagem do banner.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-height: 30px; max-width: 200px;">', obj.image.url)
        return '-'

    image_preview.short_description = 'Imagem'

    readonly_fields = ('active_image',)

    def active_image(self, obj):
        """
        Retorna uma tag HTML para exibir a imagem do banner escolhido.
        """
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;">', obj.image.url)
        return '-'

    active_image.short_description = 'Imagem Ativa'
    active_image.widget = ImagePreviewWidget_MENOR


admin.site.register(BannerMenor, BannerMenorAdmin)

