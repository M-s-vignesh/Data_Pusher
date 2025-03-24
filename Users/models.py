from django.db import models
from django.contrib.auth.models \
    import (BaseUserManager,
            AbstractBaseUser,
            AbstractUser,
            PermissionsMixin,
            )

# Create your models here.

class UserManager(BaseUserManager):
    use_in_migrations = True
    def _create_user(self, email,created_by=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        if not self.model.objects.exists():
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_staff", True)
            created_by = None
        user = self.model(
                        email=email, 
                        created_by=created_by,
                        **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email,created_by=None, password=None, **extra_fields):
        if not self.model.objects.exists():
            extra_fields.setdefault("is_superuser", True)
            extra_fields.setdefault("is_staff", True)
            created_by = None
        else:
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, created_by, password, **extra_fields)
        

    def create_superuser(self, email, created_by=None, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, created_by ,password, **extra_fields)

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True,db_index=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="created_users")
    updated_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_users")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return self.email
    

    def save(self, *args, **kwargs):
      
        request_user = kwargs.pop("request_user", None)
            
        if not self.pk and not self.created_by: 
            self.created_by = request_user

        if self.pk and request_user:  
            self.updated_by = request_user
    

        super().save(*args, **kwargs)

