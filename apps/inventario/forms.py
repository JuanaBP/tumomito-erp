from django import forms
from .models import Producto, Inventario, Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'icono', 'color', 'orden', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 2}),
            'color': forms.Select(choices=[
                ('primary', 'Azul (primary)'),
                ('success', 'Verde (success)'),
                ('warning', 'Amarillo (warning)'),
                ('danger', 'Rojo (danger)'),
                ('info', 'Celeste (info)'),
                ('secondary', 'Gris (secondary)'),
                ('dark', 'Negro (dark)'),
            ]),
        }
        help_texts = {
            'icono': 'Codigo de icono Bootstrap (ej: bi-laptop, bi-cup-hot, bi-house). Ver bootstrap-icons.com',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'activo':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()
        # color es Select
        if 'color' in self.fields:
            self.fields['color'].widget.attrs['class'] = 'form-select'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'subcategoria', 'fabricante',
                  'descripcion', 'precio_venta', 'precio_mayorista', 'cant_min_mayorista',
                  'imagen', 'destacado', 'visible_tienda', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'precio_mayorista': 'Precio para mayoristas (dejar 0 si no aplica)',
            'cant_min_mayorista': 'Cantidad minima para que aplique el precio mayorista',
            'destacado': 'Mostrar en la home de la tienda online',
            'visible_tienda': 'Visible en el catalogo publico de la tienda',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Solo categorias activas
        self.fields['categoria'].queryset = Categoria.objects.filter(activo=True)
        for name, field in self.fields.items():
            if name in ('activo', 'destacado', 'visible_tienda'):
                field.widget.attrs['class'] = 'form-check-input'
            elif name == 'imagen':
                field.widget.attrs['class'] = 'form-control'
            elif name == 'categoria':
                field.widget.attrs['class'] = 'form-select'
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()


class InventarioForm(forms.ModelForm):
    class Meta:
        model = Inventario
        fields = ['producto', 'nro_lote', 'cantidad_recibida', 'cantidad_disponible',
                  'fecha_adquision', 'fecha_emision', 'fecha_vencimiento',
                  'coste_unitario', 'coste_final']
        widgets = {
            'fecha_adquision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_emision': forms.DateInput(attrs={'type': 'date'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()
