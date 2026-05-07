from django import forms
from django.contrib.auth.models import User
from apps.core.models import Persona
from .models import Empleado, Contrato, Rol, MODULOS_SISTEMA


class RolForm(forms.ModelForm):
    """Formulario para crear/editar Roles. Permisos por checkbox de modulos."""
    modulos_seleccionados = forms.MultipleChoiceField(
        choices=MODULOS_SISTEMA,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Modulos accesibles'
    )

    class Meta:
        model = Rol
        fields = ['nombre', 'codigo', 'descripcion', 'es_admin', 'activo']
        widgets = {'descripcion': forms.Textarea(attrs={'rows': 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['modulos_seleccionados'].initial = self.instance.modulos
        for name, field in self.fields.items():
            if name in ('es_admin', 'activo'):
                field.widget.attrs['class'] = 'form-check-input'
            elif name == 'modulos_seleccionados':
                pass
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()

    def save(self, commit=True):
        rol = super().save(commit=False)
        rol.modulos = self.cleaned_data['modulos_seleccionados']
        if commit:
            rol.save()
        return rol


class EmpleadoForm(forms.Form):
    """Formulario completo: crea/edita Persona + Empleado + User."""
    # Datos personales
    nombre = forms.CharField(max_length=100, label='Nombre completo')
    ci = forms.CharField(max_length=20, label='CI')
    fecha_nacimiento = forms.DateField(label='Fecha de nacimiento',
                                       widget=forms.DateInput(attrs={'type': 'date'}))
    nacionalidad = forms.CharField(max_length=20, initial='Boliviana')
    celular = forms.CharField(max_length=20)
    email = forms.EmailField(required=False)
    direccion = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)

    # Datos laborales
    telf_contacto = forms.CharField(max_length=20, label='Telefono contacto emergencia')
    nombre_contacto = forms.CharField(max_length=60, label='Nombre contacto emergencia')
    estado_civil = forms.ChoiceField(choices=Empleado.ESTADO_CIVIL_CHOICES)
    rol = forms.ModelChoiceField(queryset=Rol.objects.filter(activo=True), label='Rol asignado')
    fecha_ingreso = forms.DateField(required=False, label='Fecha de ingreso',
                                    widget=forms.DateInput(attrs={'type': 'date'}))

    # Acceso al sistema
    username = forms.CharField(max_length=30, label='Nombre de usuario')
    password = forms.CharField(max_length=64, label='Contrasena',
                               widget=forms.PasswordInput, required=False,
                               help_text='Solo en alta. Para cambiar luego: opcion "resetear contrasena"')
    activo = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)  # Empleado existente
        super().__init__(*args, **kwargs)
        # Si es edicion, precargar
        if self.instance:
            p = self.instance.persona
            self.fields['nombre'].initial = p.nombre
            self.fields['ci'].initial = p.ci
            self.fields['fecha_nacimiento'].initial = p.fecha_nacimiento
            self.fields['nacionalidad'].initial = p.nacionalidad
            self.fields['celular'].initial = p.celular
            self.fields['email'].initial = p.email
            self.fields['direccion'].initial = p.direccion
            self.fields['telf_contacto'].initial = self.instance.telf_contacto
            self.fields['nombre_contacto'].initial = self.instance.nombre_contacto
            self.fields['estado_civil'].initial = self.instance.estado_civil
            self.fields['rol'].initial = self.instance.rol
            self.fields['fecha_ingreso'].initial = self.instance.fecha_ingreso
            self.fields['activo'].initial = self.instance.activo
            if self.instance.user:
                self.fields['username'].initial = self.instance.user.username
                self.fields['username'].disabled = True
            self.fields['password'].required = False
            self.fields['password'].help_text = 'Dejar vacio para no cambiar la contrasena'
        else:
            self.fields['password'].required = True

        # Estilo Bootstrap
        for name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs['class'] = 'form-check-input'
            elif isinstance(field, forms.ChoiceField) and not isinstance(field, forms.ModelChoiceField):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field, forms.ModelChoiceField):
                field.widget.attrs['class'] = 'form-select'
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()

    def clean_username(self):
        u = self.cleaned_data['username'].strip()
        if not self.instance:  # alta
            if User.objects.filter(username=u).exists():
                raise forms.ValidationError('Ese usuario ya existe.')
        return u

    def clean_ci(self):
        ci = self.cleaned_data['ci'].strip()
        qs = Persona.objects.filter(ci=ci)
        if self.instance:
            qs = qs.exclude(pk=self.instance.persona.pk)
        if qs.exists():
            raise forms.ValidationError('Ya existe una persona con ese CI.')
        return ci

    def save(self):
        data = self.cleaned_data
        if self.instance:
            # EDICION
            persona = self.instance.persona
            persona.nombre = data['nombre']
            persona.ci = data['ci']
            persona.fecha_nacimiento = data['fecha_nacimiento']
            persona.nacionalidad = data['nacionalidad']
            persona.celular = data['celular']
            persona.email = data['email']
            persona.direccion = data['direccion']
            persona.save()
            emp = self.instance
            emp.telf_contacto = data['telf_contacto']
            emp.nombre_contacto = data['nombre_contacto']
            emp.estado_civil = data['estado_civil']
            emp.rol = data['rol']
            emp.fecha_ingreso = data['fecha_ingreso']
            emp.activo = data['activo']
            emp.save()
            # Cambiar contrasena si se ingreso una nueva
            if emp.user and data['password']:
                emp.user.set_password(data['password'])
                emp.user.save()
            return emp
        else:
            # ALTA
            persona = Persona.objects.create(
                nombre=data['nombre'], ci=data['ci'],
                fecha_nacimiento=data['fecha_nacimiento'],
                nacionalidad=data['nacionalidad'], celular=data['celular'],
                email=data['email'] or None, direccion=data['direccion'],
            )
            user = User.objects.create_user(
                username=data['username'],
                password=data['password'],
                email=data['email'] or '',
                first_name=data['nombre'].split()[0],
            )
            emp = Empleado.objects.create(
                persona=persona, telf_contacto=data['telf_contacto'],
                nombre_contacto=data['nombre_contacto'],
                estado_civil=data['estado_civil'],
                rol=data['rol'], user=user,
                fecha_ingreso=data['fecha_ingreso'],
                activo=data['activo'],
            )
            return emp


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
        for name, field in self.fields.items():
            if isinstance(field, forms.ModelChoiceField):
                field.widget.attrs['class'] = 'form-select'
            else:
                existing = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (existing + ' form-control').strip()
