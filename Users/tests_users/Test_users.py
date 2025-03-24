from django.test import TestCase
from django.contrib.auth import get_user_model,get_user
from django.db import IntegrityError
from rest_framework.test import APIClient,APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.core.cache import cache


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


class UsersTest(APITestCase):

    def setUp(self):
        """Setup which will run before every tests"""
        self.client = APIClient() 

    def tearDown(self):
        cache.clear()
    
    def user_login(self,email=None,password=None):
            """Authenticates the user"""
            client = APIClient()
            res = client.login(email=email, 
                             password=password,)
            return res

    def test_to_register_user_first_time(self):
        '''test to register a user first time'''
        print("\nRunning test_to_register_a_user_first_time...", end="", flush=True)
        payload = {'email' : 'testuser@example.com',
                   'password' : 'pass123',
                   }
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        get_user = User.objects.get(email=payload['email'])
        self.assertTrue(get_user.is_superuser)
        self.assertEqual(get_user.email, payload['email'])
        payload = {'email' : 'testuser2@example.com',
                   'password' : 'pass123',
                   }
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        print(" ✅ Passed!")

    def test_to_login(self):
        '''test to do authentication'''
        print("\nRunning test_to_do_authentication...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        print(" ✅ Passed!")

    def test_to_logout_a_user(self):
        """Test to logout a user"""
        print("\nRunning test_to_logout_a_user...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email,
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        self.assertTrue(user1.is_authenticated)
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        user = get_user(self.client)
        self.assertFalse(user.is_authenticated)
        print(" ✅ Passed!")

    def test_to_create_normal_user_by_superuser(self):
        """Test to create a normal user by admin """
        print("\nRunning test_to_create_normal_user_by_superuser...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        self.assertTrue(user1.is_authenticated)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',}
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        get_user = User.objects.get(email=payload['email'])
        self.assertEqual(get_user.email, payload['email'])
        self.assertEqual(get_user.created_by.email, user1.email)
        self.assertFalse(get_user.is_superuser)
        print(" ✅ Passed!")

    def test_to_update_users_by_superuser(self):
        """test to update users"""
        print("\nRunning test_to_update_user_by_superuser...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        self.assertTrue(user1.is_authenticated)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',
                   }
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = {'email' : 'testuser1@example.com',
                }
        user_id = User.objects.filter(email = payload['email'])[0]
        res = self.client.put(reverse('user-detail',args=[user_id.id]),data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_mail = User.objects.filter(id =user_id.id)[0].email
        self.assertEqual(user_mail, data['email'])
        user_id.refresh_from_db()
        self.assertEqual(user_id.updated_by.email , user1.email)
        print(" ✅ Passed!")

    def test_to_do_partial_update_users_by_superuser(self):
        """Test to do parial update i.e particular field"""
        print("\nRunning test_to_do_partial_update_to_users_by_superuser...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',
                   }
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        data = {'password' : '54321',
                'email' : 'testuser@example.com',
                }
        user_id = User.objects.filter(email= payload['email'])[0]
        res = self.client.patch(reverse('user-detail',args=[user_id.id]), 
                            data, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user_id.refresh_from_db()
        self.assertEqual(user_id.updated_by.email , user1.email)
        print(" ✅ Passed!")

    def test_to_delete_superuser_by_superuser(self):
        """Test to delete a superuser account"""
        print("\nRunning test_to_delete_superuser_by_superuser...", end="", flush=True)
        user1 = create_super_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        payload = {
                   'email' : 'testuser@example.com',
                   'password' : 'pass123',
                   }
        res = self.client.post(reverse('user-list'), payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        get_user = User.objects.get(email=payload['email'])
        res = self.client.delete(reverse('user-detail',args=[get_user.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        get_user = User.objects.filter(email=payload['email'])
        self.assertEqual(len(get_user),0)
        res = self.client.delete(reverse('user-detail',args=[user1.id]))
        self.assertEqual(res.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        print(" ✅ Passed!")

    def test_to_retrive_data_by_normal_user(self):
        """Test to retrive data for normal users"""
        print("\nRunning test_to_retrive_data_by_normal_users...", end="", flush=True)
        user1 = create_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(
                                email="admin@example.com",
                                password="pass13",)
        user3 = create_user(email='user3@example.com', 
                            password='pass13')
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        Login = self.user_login(email=user2.email, 
                                password='pass13')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(reverse('user-list'))
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        print(" ✅ Passed!")

    def test_to_retrive_another_user_data_by_normal_user(self):
        """Test to retrive another user acc data by normal user"""
        print("\nRunning test_to_retrive_another_user_data_by_normal_user...", end="", flush=True)
        user1 = create_user()
        Login = self.user_login(email=user1.email, 
                                password='pass13')
        self.assertTrue(Login)
        token, _ = Token.objects.get_or_create(user=user1)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.assertTrue(user1.is_superuser)
        user2 = create_user(
                                email="admin@example.com",
                                password="pass13",)
        user3 = create_user(email='user3@example.com', 
                            password='pass13')
        res = self.client.post(reverse('logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.client.logout()
        Login = self.user_login(email=user2.email, 
                                password='pass13')
        self.assertTrue(Login)
        self.assertFalse(user2.is_superuser)
        token, _ = Token.objects.get_or_create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        res = self.client.get(reverse('user-detail',args=[user1.id]))
        self.assertEqual(res.status_code,status.HTTP_404_NOT_FOUND)
        print(" ✅ Passed!")



    