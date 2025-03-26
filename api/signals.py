from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Role
from django.db.models.signals import post_save, post_delete
from .models import Account,AccountMember
from django.core.cache import cache

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


CACHE_KEYS = "accounts_list_keys"  

def delete_cache_keys():
    keys = cache.get(CACHE_KEYS) or set()  
    for key in keys:
        cache.delete(key)
    cache.delete(CACHE_KEYS)

@receiver([post_save, post_delete], sender=Account)
def clear_account_cache(sender, **kwargs):
    delete_cache_keys()  

@receiver([post_save, post_delete], sender=AccountMember)
def clear_account_member_cache(sender, **kwargs):
    delete_cache_keys() 