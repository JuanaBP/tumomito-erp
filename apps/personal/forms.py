from django import forms
from apps.core.models import Persona
from .models import Empleado, Contrato


class EmpleadoForm(forms.Form):
    # Persona
    nombre = forms.CharField(max_length=100)
    fecha_nacimiento = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    ci = forms.CharField(max_length=20)
    nacionalidad = forms.ChoiceField(choices=Persona.NACIONALIDAD_CHOICES)
    direccion = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    celular = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    # Empleado
    telf_contacto = forms.CharField(max_length=20)
    nombre_contacto = forms.CharField(max_length=60)
    estado_civil = forms.ChoiceField(choices=Empleado.ESTADO_CIVIL_CHOICES)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()
        if self.instance:
            p = self.instance.persona
            for f in ['nombre', 'fecha_nacimiento', 'ci', 'nacionalidad',
                      'direccion', 'celular', 'email']:
                self.fields[f].initial = getattr(p, f)
            for f in ['telf_contacto', 'nombre_contacto', 'estado_civil']:
                self.fields[f].initial = getattr(self.instance, f)

    def save(self):
        d = self.cleaned_data
        if self.instance:
            persona = self.instance.persona
            for f in ['nombre', 'fecha_nacimiento', 'ci', 'nacionalidad',
                      'direccion', 'celular', 'email']:
                setattr(persona, f, d[f])
            persona.save()
            for f in ['telf_contacto', 'nombre_contacto', 'estado_civil']:
                setattr(self.instance, f, d[f])
            self.instance.save()
            return self.instance
        else:
            persona = Persona.objects.create(
                nombre=d['nombre'], fecha_nacimiento=d['fecha_nacimiento'],
                ci=d['ci'], nacionalidad=d['nacionalidad'],
                direccion=d['direccion'], celular=d['celular'], email=d['email']
            )
            return Empleado.objects.create(
                persona=persona,
                telf_contacto=d['telf_contacto'],
                nombre_contacto=d['nombre_contacto'],
                estado_civil=d['estado_civil'],
            )


class ContratoForm(forms.ModelForm):
    class Meta:
        model = Contrato
        fields = ['empleado', 'cargo_laboral', 'tipo', 'salario',
                  'fecha_inicio', 'fecha_fin', 'turno']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()
