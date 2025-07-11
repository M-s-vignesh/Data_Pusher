import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import URLValidator
import uuid

User = get_user_model()

HTTP_METHODS = [
    ("GET", "GET"),
    ("POST", "POST"),
    ("PUT", "PUT"),
    ("DELETE", "DELETE"),
]

STATUS_CHOICES = [
    ("success", "Success"),
    ("failed", "Failed"),
]

# Create your models here

class Account(models.Model):
    account_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    account_name = models.CharField(max_length=255, unique=True,db_index=True)
    app_secret_token = models.CharField(max_length=64, unique=True, editable=False)
    website = models.URLField(blank=True, null=True,db_index=True)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True)
    updated_at = models.DateTimeField(auto_now=True,db_index=True)
    created_by = models.ForeignKey(User, related_name="created_accounts", on_delete=models.CASCADE,db_index=True)
    updated_by = models.ForeignKey(User, related_name="updated_accounts", on_delete=models.SET_NULL, null=True, blank=True,db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["account_name"]),  
            models.Index(fields=["created_by"]),    
            models.Index(fields=["updated_by"]),    
            models.Index(fields=["created_at"]),    
            models.Index(fields=["updated_at"]),  
        ]
        
    def save(self, *args, **kwargs):
        if not self.app_secret_token:
            import secrets
            self.app_secret_token = secrets.token_hex(32)

        request_user = kwargs.pop("request_user", None)
            
        if not self.pk and not self.created_by: 
            self.created_by = request_user

        if self.pk and request_user:  
            self.updated_by = request_user

        super().save(*args, **kwargs)

    def __str__(self):
        return self.account_name
    
class Role(models.Model):
    ROLE_CHOICES = [
        ("Admin", "Admin"),
        ("Normal User", "Normal User"),
    ]

    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.role_name
    

class AccountMember(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, db_index=True)  
    user = models.ForeignKey(User, on_delete=models.PROTECT, db_index=True)  
    role = models.ForeignKey(Role, on_delete=models.CASCADE, db_index=True)  
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)  
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_members", db_index=True)
    updated_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="updated_members",null=True,blank=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["account", "user"]),  
            models.Index(fields=["created_at"]),  
        ]
        unique_together = ("account", "user")  

    def __str__(self):
        return f"{self.user} - {self.role} in {self.account}"
    
    def save(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
            
        if not self.pk and not self.created_by: 
            self.created_by = request_user

        if self.pk and request_user:  
            self.updated_by = request_user

        super().save(*args, **kwargs)


class Destination(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='destinations')
    url = models.URLField(validators=[URLValidator()], unique=True)
    http_method = models.CharField(max_length=10, choices=HTTP_METHODS)
    headers = models.JSONField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_destinations')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='updated_destinations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account} - {self.url}"
    
    def save(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
            
        if not self.pk and not self.created_by: 
            self.created_by = request_user

        if self.pk and request_user:  
            self.updated_by = request_user

        super().save(*args, **kwargs)

class Log(models.Model):
    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='logs')
    destination = models.ForeignKey(Destination, on_delete=models.CASCADE, related_name='logs')
    received_timestamp = models.DateTimeField(auto_now_add=True)
    processed_timestamp = models.DateTimeField(null=True, blank=True)
    received_data = models.JSONField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Event {self.event_id} - Status {self.status}"