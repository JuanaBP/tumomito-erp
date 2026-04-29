from django import forms
from .models import Proveedor


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['empresa', 'nit', 'representante_legal', 'pais',
                  'direccion', 'telefono', 'email', 'activo']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name == 'activo':
                field.widget.attrs['class'] = 'form-check-input'
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()
