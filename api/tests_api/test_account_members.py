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

class AccountMemberTests(TestCase):
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
    
    def test_to_create_account_member(self):
        """Test to create account member"""
        print("\nRunning test_to_create_an_account...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(created_by=user1)
        user3 = create_user(email='Test@example.com',created_by=user1)
        user4 = create_user(email='Test4@example.com',created_by=user1)
        user5 = create_user(email='Test5@example.com',created_by=user1)
        account = create_account(created_by=user1)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 1,
                   }
        res = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload2 = {'account' : account.id,
                   'user' : user3.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'), payload2, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        Login = self.user_login(email=user2.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        member = AccountMember.objects.filter(user=user2)
        self.assertTrue(member.exists())
        members = AccountMember.objects.filter(account = account.id).values_list("user_id", flat=True)
        role = True if member.first().role.id == 1 else False
        self.assertTrue(role)
        payload = {'account' : account.id,
                   'user' : user4.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        Login = self.user_login(email=user4.email, 
                                password='pass13')
        self.assertTrue(Login) 
        token, _ = Token.objects.get_or_create(user=user4)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        member = AccountMember.objects.filter(user=user4)
        self.assertTrue(member.exists())
        role = True if member.first().role.id == 1 else False
        self.assertFalse(role)
        payload = {'account' : account.id,
                   'user' : user4.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        Login = self.user_login(email=user5.email, 
                                password='pass13')
        self.assertTrue(Login) 
        token, _ = Token.objects.get_or_create(user=user5)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        member = AccountMember.objects.filter(user=user5)
        self.assertFalse(member.exists())
        payload = {'account' : account.id,
                   'user' : user5.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print(" ✅ Passed!")

    def test_to_retrive_account_members(self):
        """Test to fetch account member"""
        print("\nRunning test_to_retrive_account_members...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(created_by=user1)
        user3 = create_user(email='Test@example.com',created_by=user1)
        user4 = create_user(email='Test4@example.com',created_by=user1)
        user5 = create_user(email='Test5@example.com',created_by=user1)
        account = create_account(created_by=user1)
        account1 = create_account(account_name='Financial Account',
                                    created_by=user1)
        account2 = create_account(account_name='Dummy Account',
                                    created_by=user1)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 1,
                   }
        res = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload2 = {'account' : account1.id,
                   'user' : user3.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'), payload2, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        res = self.client.get(reverse('account_member-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)
        res = self.client.post(reverse('logout'))
        self.client.logout()
        Login = self.user_login(email=user2.email, 
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(reverse('account_member-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 2)
        res = self.client.post(reverse('logout'))
        self.client.logout()
        Login = self.user_login(email=user3.email, 
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(reverse('account_member-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()), 1)
        res = self.client.post(reverse('logout'))
        self.client.logout()
        Login = self.user_login(email=user5.email, 
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=user5)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(reverse('account_member-list'))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        print(" ✅ Passed!")

    def test_to_update_account_members(self):
        """Test to update account member"""
        print("\nRunning test_to_update_account_member...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(created_by=user1)
        user3 = create_user(email='Test@example.com',created_by=user1)
        user4 = create_user(email='Test4@example.com',created_by=user1)
        user5 = create_user(email='Test5@example.com',created_by=user1)
        account = create_account(created_by=user1)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 2,
                   }
        res1 = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload2 = {'account' : account.id,
                   'user' : user3.id,
                   'role' : 2,
                   }
        res3 = self.client.post(reverse('account_member-list'), payload2, format='json')
        updated_data = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 1,
                   }
        res2 = self.client.put(reverse('account_member-detail',args=[res1.json()['id']]),updated_data, format='json')
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        role_id = AccountMember.objects.filter(account=account.id,user = user2).first().role.id
        self.assertEqual(1,role_id)
        res = self.client.post(reverse('logout'))
        Login = self.user_login(email=user3.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        updated_data = {'account' : account.id,
                   'user' : user3.id,
                   'role' : 1,
                   }
        res4 = self.client.put(reverse('account_member-detail',args=[res3.json()['id']]),updated_data, format='json')
        self.assertEqual(res4.status_code, status.HTTP_403_FORBIDDEN)
        role_id = AccountMember.objects.filter(account=account.id,user = user3).first().role.id
        self.assertEqual(2,role_id)
        print(" ✅ Passed!")

    def test_to_delete_account_members(self):
        """Test to delete  account member"""
        print("\nRunning test_to_delete_account_member...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(created_by=user1)
        user3 = create_user(email='Test@example.com',created_by=user1)
        user4 = create_user(email='Test4@example.com',created_by=user1)
        user5 = create_user(email='Test5@example.com',created_by=user1)
        account = create_account(created_by=user1)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 2,
                   }
        res1 = self.client.post(reverse('account_member-list'), payload, format='json')
        self.assertEqual(res1.status_code, status.HTTP_201_CREATED)
        payload2 = {'account' : account.id,
                   'user' : user3.id,
                   'role' : 1,
                   }
        res2 = self.client.post(reverse('account_member-list'), payload2, format='json')
        self.assertEqual(res2.status_code, status.HTTP_201_CREATED)
        payload3 = {'account' : account.id,
                   'user' : user4.id,
                   'role' : 2,
                   }
        res3 = self.client.post(reverse('account_member-list'), payload3, format='json')
        self.assertEqual(res3.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(AccountMember.objects.all()),3)
        delete = self.client.delete(reverse('account_member-detail',args=[res1.json()['id']]))
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(AccountMember.objects.all()),2)
        res = self.client.post(reverse('logout'))
        self.client.logout()
        Login = self.user_login(email=user4.email, 
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=user4)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        delete = self.client.delete(reverse('account_member-detail',args=[res2.json()['id']]))
        self.assertEqual(delete.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(len(AccountMember.objects.all()),2)
        res = self.client.post(reverse('logout'))
        self.client.logout()
        Login = self.user_login(email=user3.email, 
                                password='pass13')
        token, _ = Token.objects.get_or_create(user=user3)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        delete = self.client.delete(reverse('account_member-detail',args=[res3.json()['id']]))
        self.assertEqual(delete.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(AccountMember.objects.all()),1)
        print(" ✅ Passed!")

    def test_to_add_same_user_to_same_account(self):
        """Test to add same user to same account"""
        print("\nRunning test_to_add_same_user_to_same_account...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(created_by=user1)
        account = create_account(created_by=user1)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 1,
                   }
        res = self.client.post(reverse('account_member-list'),payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        payload = {'account' : account.id,
                   'user' : user2.id,
                   'role' : 2,
                   }
        res = self.client.post(reverse('account_member-list'),payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        print(" ✅ Passed!")
    