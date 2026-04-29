from django import forms
from apps.core.models import Persona
from .models import Cliente


class ClienteForm(forms.Form):
    # Datos de Persona
    nombre = forms.CharField(max_length=100, label="Nombre completo")
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de nacimiento"
    )
    ci = forms.CharField(max_length=20, label="CI")
    nacionalidad = forms.ChoiceField(choices=Persona.NACIONALIDAD_CHOICES)
    direccion = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
    celular = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    # Datos de Cliente
    nit = forms.CharField(max_length=20, label="NIT")
    razon_social = forms.CharField(max_length=60, required=False, label="Razon Social")

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing + ' form-control').strip()

        if self.instance:
            p = self.instance.persona
            self.fields['nombre'].initial = p.nombre
            self.fields['fecha_nacimiento'].initial = p.fecha_nacimiento
            self.fields['ci'].initial = p.ci
            self.fields['nacionalidad'].initial = p.nacionalidad
            self.fields['direccion'].initial = p.direccion
            self.fields['celular'].initial = p.celular
            self.fields['email'].initial = p.email
            self.fields['nit'].initial = self.instance.nit
            self.fields['razon_social'].initial = self.instance.razon_social

    def save(self):
        data = self.cleaned_data
        if self.instance:
            persona = self.instance.persona
            persona.nombre = data['nombre']
            persona.fecha_nacimiento = data['fecha_nacimiento']
            persona.ci = data['ci']
            persona.nacionalidad = data['nacionalidad']
            persona.direccion = data['direccion']
            persona.celular = data['celular']
            persona.email = data['email']
            persona.save()
            cliente = self.instance
            cliente.nit = data['nit']
            cliente.razon_social = data['razon_social']
            cliente.save()
        else:
            persona = Persona.objects.create(
                nombre=data['nombre'],
                fecha_nacimiento=data['fecha_nacimiento'],
                ci=data['ci'],
                nacionalidad=data['nacionalidad'],
                direccion=data['direccion'],
                celular=data['celular'],
                email=data['email'],
            )
            cliente = Cliente.objects.create(
                persona=persona,
                nit=data['nit'],
                razon_social=data['razon_social'],
            )
        return cliente
