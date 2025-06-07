from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

ROLES_CHOICES = (
    ('administrador', 'Administrador'),
    ('doctor', 'Doctor'),
    ('secretaria', 'Secretaria'),
    ('usuario', 'Usuario')
)

class UsuarioManager(BaseUserManager):
    def create_user(self, email, usuario, nombre, apellido, password, **extra_fields):
        if not usuario:
            raise ValueError('El campo de usuario es obligatorio')
        if not email:
            raise ValueError('El campo de correo electrónico es obligatorio')
        usuario = self.model(
            usuario=usuario,
            email = self.normalize_email(email),
            nombre = nombre,
            apellido = apellido,
            **extra_fields
            )
        
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario
    
    def create_superuser(self, usuario, email, nombre, apellido, password, **extra_fields):
        usuario = self.create_user(
            email,
            usuario,
            nombre,
            apellido,
            password,
            **extra_fields
            )
        
        usuario.usuario_administrador = True
        usuario.rol = 'administrador'
        usuario.save(using=self._db)
        return usuario




class Usuario(AbstractBaseUser):
    usuario = models.CharField("Nombre de usuario", unique = True, max_length=100)
    email = models.EmailField("Correo electrónico", max_length=254, unique=True)
    nombre = models.CharField("Nombres", max_length=200, blank=True, null=True)
    apellido = models.CharField("Apellidos", max_length=200, blank=True, null=True)
    rol = models.CharField( "Rol del usuario",
        max_length=20,
        choices=ROLES_CHOICES,
        default='usuario',
        blank=False,
        null=False
    )
    objects = UsuarioManager()

    usuario_activo = models.BooleanField(default = True)
    usuario_administrador = models.BooleanField(default = False)

    USERNAME_FIELD = 'usuario'
    REQUIRED_FIELDS = ['email','nombre','apellido']

    def __str__(self):
        return f'{self.usuario}'
    
    def has_perm(self, perm, obj = None):
        return True
    
    def has_module_perms(self, app_label):
        return True
    
    @property
    def is_staff(self):
        return self.usuario_administrador
    