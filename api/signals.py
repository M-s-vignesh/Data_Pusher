from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    """
    Ensure 'Admin' and 'Normal User' roles exist in the database.
    This runs after migrations are applied.
    """
    if sender.name != "api":  
        return
    roles_to_create = ['Admin', 'Normal User']

    for role_name in roles_to_create:
        Role.objects.get_or_create(role_name=role_name)

    print("✅ Default roles ensured in the database.")
