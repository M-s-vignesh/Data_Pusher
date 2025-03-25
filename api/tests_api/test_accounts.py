from django.test import TestCase
from django.contrib.auth import get_user_model,get_user
from django.db import IntegrityError
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from api.models import Account


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
                    email='test@example.com',
                    password='pass13'):
        """Function to create super user"""
        user = User.objects.create_superuser(
                                        email=email,
                                        password=password,
                                        created_by=created_by)
        return user


class AccountTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
    def tearDown(self):
        cache.clear()
    
    def user_login(self,email=None,password=None):
            """Authenticates the user"""
            client = APIClient()
            res = client.login(email=email, 
                             password=password,)
            return res
    
    def test_to_create_an_account(self):
        """Test to create an account"""
        print("\nRunning test_to_create_an_account...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                    'account_name': 'Test Account',
                    'website': 'https://example.com',
                    }
        res = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Account.objects.count(), 1)
        acc = Account.objects.get(account_id = res.json()['account_id'])
        self.assertEqual(acc.created_by.email, user1.email)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user2 = User.objects.filter(email=payload['email'])[0]
        Login = self.user_login(email=user2.email, 
                                password='pass123')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        payload2 = {
                    'account_name': 'Test Account 2',
                    'website': 'https://example.com',
                    }
        res = self.client.post(reverse('account-list'), payload2, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Account.objects.count(), 1)
        exists = Account.objects.filter(account_name=payload2['account_name']).exists()
        self.assertFalse(exists)
        print(" ✅ Passed!")

    def test_to_retrive_accounts(self):
        print("\nRunning test_to_retrive_accounts...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                    'account_name': 'Test Account',
                    'website': 'https://example.com',
                    }
        res = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 2',
                    'website': 'https://example.com',}
        res = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 3',
                    'website': 'https://example.com',}
        res = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res= self.client.get(reverse('account-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 3)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user2 = User.objects.filter(email=payload['email'])[0]
        Login = self.user_login(email=user2.email, 
                                password='pass123')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res= self.client.get(reverse('account-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 3)
        print(" ✅ Passed!")

    def test_to_update_accounts(self):
        print("\nRunning test_to_update_accounts...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                    'account_name': 'Test Account',
                    'website': 'https://example.com',
                    }
        res1 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 2',
                    'website': 'https://example.com',}
        res2 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 3',
                    'website': 'https://example.com',}
        res3 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        update_data = {'account_name': 'Updated Account',
                    'website': 'https://example.com',}
        acc_id = res1.json()['account_id']
        update = self.client.put(reverse('account-detail',args=[acc_id]),
                                 update_data, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        acc = Account.objects.get(account_id=acc_id)
        self.assertEqual(acc.account_name, update_data['account_name'])
        self.assertEqual(acc.updated_by.email, user1.email)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user2 = User.objects.filter(email=payload['email'])[0]
        Login = self.user_login(email=user2.email, 
                                password='pass123')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        updated_data = {'account_name': 'Banking Account',
                    'website': 'https://example.com',}
        acc_id = res2.json()['account_id']
        update = self.client.put(reverse('account-detail',args=[acc_id]),
                                 updated_data, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        acc = Account.objects.get(account_id=acc_id)
        self.assertEqual(acc.account_name, updated_data['account_name'])
        self.assertEqual(acc.updated_by.email, payload['email'])
        print(" ✅ Passed!")

    def test_to_do_partial_update_to_accounts(self):
        print("\nRunning test_to_do_partial_update_to_accounts...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                    'account_name': 'Test Account',
                    'website': 'https://example.com',
                    }
        res1 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 2',
                    'website': 'https://example.com',}
        res2 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        update_data = {
                    'website': 'https://example2.com',}
        acc_id = res1.json()['account_id']
        update = self.client.patch(reverse('account-detail',args=[acc_id]),
                                 update_data, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        acc = Account.objects.get(account_id=acc_id)
        self.assertEqual(acc.website, update_data['website'])
        self.assertEqual(acc.updated_by.email, user1.email)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user2 = User.objects.filter(email=payload['email'])[0]
        Login = self.user_login(email=user2.email, 
                                password='pass123')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        updated_data = {'account_name': 'Banking Account',}
        acc_id = res2.json()['account_id']
        update = self.client.patch(reverse('account-detail',args=[acc_id]),
                                 updated_data, format='json')
        self.assertEqual(update.status_code, status.HTTP_200_OK)
        acc = Account.objects.get(account_id=acc_id)
        self.assertEqual(acc.account_name, updated_data['account_name'])
        self.assertEqual(acc.updated_by.email, payload['email'])
        self.assertEqual(acc.created_by.email, user1.email)
        print(" ✅ Passed!")

    def test_to_delete_accounts(self):
        print("\nRunning test_to_delete_accounts...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                    'account_name': 'Test Account',
                    'website': 'https://example.com',
                    }
        res1 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload = {
                   'account_name': 'Test Account 2',
                    'website': 'https://example.com',}
        res2 = self.client.post(reverse('account-list'), payload, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        cnt = Account.objects.all().count()
        self.assertEqual(2, cnt)
        delete = self.client.delete(reverse('account-detail',args=[res1.json()['account_id']]))
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Account.objects.all().count(), 1)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user2 = User.objects.filter(email=payload['email'])[0]
        Login = self.user_login(email=user2.email, 
                                password='pass123')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        nor_delete = self.client.delete(reverse('account-detail',args=[res2.json()['account_id']]))
        self.assertEqual(nor_delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Account.objects.all().count(), 1)
        print(" ✅ Passed!")