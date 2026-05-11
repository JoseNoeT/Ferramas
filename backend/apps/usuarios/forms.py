from django import forms

from .models import Usuario


ROLES_INTERNOS = [
    (Usuario.Rol.VENDEDOR, "Vendedor"),
    (Usuario.Rol.BODEGUERO, "Bodeguero"),
    (Usuario.Rol.CONTADOR, "Contador"),
    (Usuario.Rol.ADMIN, "Administrador"),
]


class RegistroForm(forms.Form):
    """Formulario de registro para nuevos usuarios."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com", "autocomplete": "email"}),
    )
    password1 = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"placeholder": "Minimo 8 caracteres", "autocomplete": "new-password"}),
        min_length=8,
    )
    password2 = forms.CharField(
        label="Confirmar contrasena",
        widget=forms.PasswordInput(attrs={"placeholder": "Repite tu contrasena", "autocomplete": "new-password"}),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese email.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contrasenas no coinciden.")
        return cleaned_data


class LoginForm(forms.Form):
    """Formulario de autenticacion de usuarios."""

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "correo@ejemplo.com", "autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(attrs={"placeholder": "Tu contrasena", "autocomplete": "current-password"}),
    )


class UsuarioInternoCreateForm(forms.ModelForm):
    password_temporal = forms.CharField(
        label="Contrasena temporal",
        min_length=8,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Minimo 8 caracteres",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = Usuario
        fields = ["email", "rol", "activo", "password_temporal"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rol"].choices = ROLES_INTERNOS

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise forms.ValidationError("El email es obligatorio.")
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean_rol(self):
        rol = self.cleaned_data.get("rol")
        if rol not in dict(ROLES_INTERNOS):
            raise forms.ValidationError("Debes seleccionar un rol interno valido.")
        return rol




# Formulario para edición básica del perfil de usuario autenticado
from django.core.exceptions import ValidationError

class PerfilUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["email"]

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise forms.ValidationError("El email es obligatorio.")
        queryset = Usuario.objects.filter(email=email)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email


# Restaurar UsuarioInternoUpdateForm para no romper imports existentes
class UsuarioInternoUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["email", "rol", "activo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["rol"].choices = ROLES_INTERNOS

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise forms.ValidationError("El email es obligatorio.")
        queryset = Usuario.objects.filter(email=email)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Ya existe un usuario con ese email.")
        return email

    def clean_rol(self):
        rol = self.cleaned_data.get("rol")
        if rol not in dict(ROLES_INTERNOS):
            raise forms.ValidationError("Debes seleccionar un rol interno valido.")
        return rol
