from django.test import TestCase
from django.contrib.auth import get_user_model,get_user
from django.db import IntegrityError
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from api.models import Account, AccountMember

User = get_user_model()

def create_user(email='test@example.com',
                password='pass13',
                created_by=None):
        """Function to create normal user"""
        user = User.objects.create_user(
                                        email=email,
                                        password=password,
                                        created_by=created_by)
        return user

def create_super_user(created_by=None,
                    email='testuser@example.com',
                    password='pass13'):
        """Function to create super user"""
        user = User.objects.create_superuser(
                                        email=email,
                                        password=password,
                                        created_by=created_by)
        return user

def create_account(account_name= 'Test Account',
                    website= 'https://example.com',
                    created_by = None):
    """Creating an account """
    acc = Account.objects.create(account_name=account_name,
                                 website=website,
                                 created_by=created_by)
    return acc

class AccountTests(TestCase):
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user1 = create_super_user()
        Login = self.user_login(email=self.user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=self.user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(self.user1.is_superuser)
        self.user2 = create_user(created_by=self.user1)
        self.user3 = create_user(email='Test@example.com',created_by=self.user1)
        self.user4 = create_user(email='Test4@example.com',created_by=self.user1)
        self.user5 = create_user(email='Test5@example.com',created_by=self.user1)
        self.account1 = create_account(created_by=self.user1)
        self.account2 = create_account(account_name="Banking",created_by=self.user1)
        self.account3 = create_account(account_name="Dummy",created_by=self.user1)
        payload1 = {'account' : self.account1.id,
                   'user' : self.user2.id,
                   'role' : 1,
                   }
        payload2 = {'account' : self.account2.id,
                   'user' : self.user3.id,
                   'role' : 2,
                   }
        self.res1 = self.client.post(reverse('account_member-list'), payload1, format='json')
        self.res2 = self.client.post(reverse('account_member-list'), payload2, format='json')
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()

    def user_login(self,email=None,password=None):
            """Authenticates the user"""
            client = APIClient()
            res = client.login(email=email, 
                             password=password,)
            return res
    
    def tearDown(self):
        cache.clear()

    def test_admin_can_create_account(self):
        print("\nRunning test_admin_can_create_account...", end="", flush=True)
        Login = self.user_login(email=self.user2.email,
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=self.user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        payload = {"account_name": "New Admin Account"}
        response = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Account.objects.filter(account_name="New Admin Account").exists())
        print(" ✅ Passed!")

    def test_normal_user_cannot_create_account(self):
        print("\nRunning test_normal_user_cannot_create_account...", end="", flush=True)
        self.client.force_authenticate(user=self.user3)
        payload = {"account_name": "User Created Account"}
        response = response = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print(" ✅ Passed!")

    def test_associated_user_can_update_account(self):
        print("\nRunning test_associated_user_can_update_account...", end="", flush=True)
        self.client.force_authenticate(user=self.user3)
        payload = {"account_name": "Updated User Account"}
        acc_id = Account.objects.filter(id=self.res2.json()['account'])[0]
        response = self.client.put(reverse('account-detail',args=[acc_id.account_id]), payload,format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        acc_id.refresh_from_db()
        self.assertEqual(acc_id.account_name, "Updated User Account")
        print(" ✅ Passed!")

    def test_unassociated_user_cannot_update_account(self):
        print("\nRunning test_unassociated_user_cannot_update_account...", end="", flush=True)
        self.client.force_authenticate(user=self.user4)
        payload = {"account_name": "Unauthorized Update"}
        acc_id = Account.objects.filter(id=self.res2.json()['account'])[0]
        response = self.client.put(reverse('account-detail',args=[acc_id.account_id]), payload,format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        print(" ✅ Passed!")

    def test_admin_can_delete_account(self):
        print("\nRunning test_admin_can_delete_account...", end="", flush=True)
        self.client.force_authenticate(user=self.user2)
        acc_id = Account.objects.filter(id=self.res2.json()['account'])[0]
        response = self.client.delete(reverse('account-detail',args=[acc_id.account_id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Account.objects.filter(account_id=acc_id.account_id).exists())
        print(" ✅ Passed!")

    def test_normal_user_cannot_delete_account(self):
        print("\nRunning test_normal_user_cannot_delete_account...", end="", flush=True)
        self.client.force_authenticate(user=self.user3)
        acc_id = Account.objects.filter(id=self.res2.json()['account'])[0]
        response = self.client.delete(reverse('account-detail',args=[acc_id.account_id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Account.objects.filter(account_id=acc_id.account_id).exists())
        print(" ✅ Passed!")

    def test_list_accounts_based_on_role(self):
        print("\nRunning test_list_accounts_based_on_role...", end="", flush=True)
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(reverse('account-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['account_name'], "Banking")
        print(" ✅ Passed!")

    def test_cache_stores_accounts_list(self):
        print("\nRunning test_cache_stores_accounts_list...", end="", flush=True)
        self.client.force_authenticate(user=self.user2)
        response1 = self.client.get(reverse('account-list'))
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        cached_response = cache.get(f"accounts_list_{self.user2.id}_")
        self.assertIsNotNone(cached_response)
        print(" ✅ Passed!")
    