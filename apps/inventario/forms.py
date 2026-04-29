from django import forms
from .models import Producto, Inventario


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['codigo', 'nombre', 'categoria', 'subcategoria', 'fabricante',
                  'descripcion', 'precio_venta', 'imagen', 'activo']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'activo':
                field.widget.attrs['class'] = 'form-check-input'
            elif name == 'imagen':
                field.widget.attrs['class'] = 'form-control'
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
