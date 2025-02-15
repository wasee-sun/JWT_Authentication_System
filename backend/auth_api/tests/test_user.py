import os, io, json
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils.timezone import now, timedelta
from PIL import Image
from rest_framework import status
from rest_framework.response import Response
from rest_framework.exceptions import Throttled
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework.test import APITestCase, APIClient
from social_core.exceptions import AuthException
from datetime import datetime, timedelta, timezone
from unittest.mock import patch


CSRF_TOKEN_URL = reverse('csrf-token')
RECAPTCHA_VERIFY_URL = reverse('recaptcha-verify')
LOGIN_URL = reverse('login')
RESEND_OTP_URL = reverse('resend-otp')
TOKEN_USER_URL = reverse('token')
TOKEN_REFRESH_URL = reverse('token-refresh')
VERIFY_EMAIL_URL = reverse('email-verify')
VERIFY_PHONE_URL = reverse('phone-verify')
RESET_PASSWORD_URL = reverse('password-reset')
USER_URL = reverse('user-list')
SOCIAL_LOGIN_URL = reverse('social-auth')
LOGOUT_URL = reverse('logout')

def generate_otp():
    return 123456

def detail_url(user_id):
    """Create and return a user detail URL"""
    return reverse('user-detail', args=[user_id])

def image_upload_url(user_id):
    """Create and return a user image upload URL"""
    return reverse('user-upload-image', args=[user_id])

def deactivate_user_url(user_id):
    """Deactivate user URL"""
    return reverse('user-deactivate-user', args=[user_id])

def activate_user_url(user_id):
    """Activate user URL"""
    return reverse('user-activate-user', args=[user_id])

def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)

# class CSRFTokenViewTests(APITestCase):
#     """Test the CSRFTokenView"""
    
#     def setUp(self):
#         self.client = APIClient()
    
#     def test_get_csrf_token_success(self):
#         """
#         Test that the view successfully returns a CSRF token and expiry.
#         """
#         response = self.client.get(CSRF_TOKEN_URL)

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('csrf_token', response.data)
#         self.assertIn('csrf_token_expiry', response.data)

#         # Validate the expiry is a valid datetime and is in the future (approximately 1 day)
#         try:
#             expiry = datetime.fromisoformat(response.data['csrf_token_expiry'].replace('Z', '+00:00'))  # Handle the Z for timezone
#         except ValueError:
#             self.fail("csrf_token_expiry is not a valid datetime format")

#         expected_expiry_min = now() + timedelta(days=0.9)
#         expected_expiry_max = now() + timedelta(days=1.1)  # Give a bit of leeway

#         self.assertTrue(expected_expiry_min <= expiry <= expected_expiry_max, "Expiry is not approximately 1 day from now")

#         # Validate that the csrf token is not empty:
#         self.assertTrue(len(response.data['csrf_token']) > 0)

#     @patch('auth_api.views.get_token')
#     def test_get_csrf_token_internal_server_error(self, mock_get_token):
#         """
#         Test that the view returns a 500 error when get_token raises an exception.
#         """
#         mock_get_token.side_effect = Exception("Simulated error")  # Simulate an error
#         response = self.client.get(CSRF_TOKEN_URL)

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Simulated error")

# class RecaptchaValidationViewTests(APITestCase):
#     """Test the RecaptchaValidationView"""
    
#     def setUp(self):
#         self.client = APIClient()
    
#     @patch('auth_api.views.requests.post')
#     def test_recaptcha_validation_success(self, mock_post):
#         """
#         Test that the view returns a success message when reCAPTCHA validation is successful.
#         """
#         mock_post.return_value.json.return_value = {'success': True}
#         mock_post.return_value.status_code = 200

#         data = {'recaptcha_token': 'valid_token'}
#         response = self.client.post(RECAPTCHA_VERIFY_URL, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('success', response.data)
#         self.assertEqual(response.data['success'], 'reCAPTCHA validation successful.')

#     @patch('auth_api.views.requests.post')
#     def test_recaptcha_validation_failure(self, mock_post):
#         """
#         Test that the view returns an error message when reCAPTCHA validation fails.
#         """
#         mock_post.return_value.json.return_value = {'success': False}
#         mock_post.return_value.status_code = 200


#         data = {'recaptcha_token': 'invalid_token'}
#         response = self.client.post(RECAPTCHA_VERIFY_URL, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid reCAPTCHA token.')

#     @patch('auth_api.views.requests.post')
#     def test_recaptcha_validation_invalid_json(self, mock_post):
#         """
#         Test that the view returns an error message when the reCAPTCHA service returns invalid JSON.
#         """
#         mock_post.return_value.json.side_effect = json.JSONDecodeError("Simulated JSON error", "doc", 0)
#         mock_post.return_value.status_code = 200

#         data = {'recaptcha_token': 'some_token'}
#         response = self.client.post(RECAPTCHA_VERIFY_URL, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid JSON.')

#     @patch('auth_api.views.requests.post')
#     def test_recaptcha_validation_internal_server_error(self, mock_post):
#         """
#         Test that the view returns a 500 error when an unexpected exception occurs.
#         """
#         mock_post.side_effect = Exception("Simulated internal server error")

#         data = {'recaptcha_token': 'some_token'}
#         response = self.client.post(RECAPTCHA_VERIFY_URL, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertIn("Simulated internal server error", response.data['error'])

# class LoginViewTests(APITestCase):
#     """Test the LoginView"""

#     def setUp(self):
#         self.url = LOGIN_URL
#         self.test_user = create_user(
#             email='test@example.com',
#             password='TestP@ssw0rd',
#             is_active=True,
#             is_email_verified=True
#         )
#         self.client = APIClient()
        
#     def tearDown(self):
#         cache.clear()

#     @patch('auth_api.views.create_otp')
#     def test_login_success(self, mock_create_otp):
#         """
#         Test successful login returns 200 OK and the expected data.
#         """
#         # Return a proper Response object instead of a MagicMock
#         mock_create_otp.return_value = Response(
#             {'success': 'Email sent', 'otp': True, 'user_id': self.test_user.id},
#             status=status.HTTP_200_OK
#         )

#         data = {'email': 'test@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['success'], 'Email sent')
#         self.assertEqual(response.data['otp'], True)
#         self.assertEqual(response.data['user_id'], self.test_user.id)

#     def test_login_missing_credentials(self):
#         """
#         Test that missing email or password returns 400 Bad Request.
#         """
#         data = {'email': 'test@example.com'}  # Missing password
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Email and password are required")

#         data = {'password': 'TestP@ssw0rd'}  # Missing email
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Email and password are required")

#     def test_login_invalid_email(self):
#         """
#         Test that invalid credentials (wrong password) return 400 Bad Request.
#         """
#         data = {'email': 'test2@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Invalid credentials")
        
#     def test_login_invalid_credentials(self):
#         """
#         Test that invalid credentials (wrong password) return 400 Bad Request.
#         """
#         data = {'email': 'test@example.com', 'password': 'wrongpassword'}
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Invalid credentials")

#     def test_login_unverified_email(self):
#         """Test case for login with unverified email."""
#         # Create a test user with an unverified email address
#         unverified_user = create_user(
#             email='unverified@example.com',
#             password='TestP@ssw0rd',
#             is_active=True,
#             is_email_verified=False  # Set is_verified to False
#         )

#         data = {'email': 'unverified@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Or whatever status code you return
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Email is not verified. You must verify your email first")

#     def test_login_inactive_account(self):
#         """Test case for login with an inactive account."""
#         # Create a test user with an inactive account
#         inactive_user = create_user(
#             email='inactive@example.com',
#             password='TestP@ssw0rd',
#             is_active=False,  # Set is_active to False
#             is_email_verified=True
#         )

#         data = {'email': 'inactive@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Or whatever status code you return
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Account is deactivated. Contact your admin")
        
#     def test_login_auth_not_email(self):
#         """Test case for login with an inactive account."""
#         # Create a test user with an inactive account
#         diff_auth_user = create_user(
#             email='diffauth@example.com',
#             password='TestP@ssw0rd',
#             is_active=False,  # Set is_active to False
#             is_email_verified=True,
#             auth_provider='google'
#         )

#         data = {'email': 'diffauth@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')
        
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Or whatever status code you return
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], f"This process cannot be used, as user is created using {diff_auth_user.auth_provider}")

#     @patch('auth_api.views.EmailOtp.send_email_otp')
#     def test_login_otp_failure_bad_request(self, mock_send_email):
#         """
#         Test that if sending the OTP email fails (i.e., EmailOtp.send_email_otp returns False),
#         the LoginView returns a 400 Bad Request with the expected error message.
#         """
#         # Arrange: simulate the failure of sending the OTP email by returning False.
#         mock_send_email.return_value = False

#         data = {'email': 'test@example.com', 'password': 'TestP@ssw0rd'}
#         # Act: perform a POST request to the login view.
#         response = self.client.post(self.url, data, format='json')

#         # Assert: verify that the view returns a 400 response and the correct error message.
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(
#             response.data['error'],
#             "Something went wrong, could not send OTP. Try again"
#         )
    
#     @patch('auth_api.views.create_otp')
#     def test_login_otp_failure(self, mock_create_otp):
#         """
#         Test that a failure during OTP creation returns 500 Internal Server Error.
#         """
#         mock_create_otp.side_effect = Exception("Simulated OTP creation error")

#         data = {'email': 'test@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertIn("Simulated OTP creation error", response.data['error']) # Verify the error message

#     @patch('auth_api.views.create_otp')
#     def test_login_internal_server_error(self, mock_create_otp):
#         """
#         Test for a generic internal server error within the view.
#         """
#         # Simulate an internal error in create_otp.
#         mock_create_otp.side_effect = Exception("Simulated Internal Server Error")

#         data = {'email': 'test@example.com', 'password': 'TestP@ssw0rd'}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertIn("Simulated Internal Server Error", response.data['error'])

#     @patch('auth_api.views.check_user_validity')
#     def test_login_throttled(self, mock_check_user_validity):
#         """
#         Test that the login view is throttled after exceeding the rate limit,
#         considering the caching mechanism.
#         """

#         mock_check_user_validity.return_value = self.test_user
#         data = {'email': 'test@example.com', 'password': 'TestP@ssw0rd'}

#         # ** Crucial: Seed the cache for the throttle to work
#         cache.set(f"id_{self.test_user.id}", self.test_user.id, timeout=60)

#         # Make the first request (should succeed)
#         response1 = self.client.post(self.url, data, format='json')
#         self.assertEqual(response1.status_code, status.HTTP_200_OK)

#         # Make the second request immediately (should be throttled)
#         response2 = self.client.post(self.url, data, format='json')
#         self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#         self.assertIn('detail', response2.data)
       
# class ResendOtpViewTests(APITestCase): 
#     """Test the ResendOtpView"""

#     def setUp(self):
#         self.client = APIClient()
#         self.url = RESEND_OTP_URL
#         self.test_user = create_user(
#             email='test@example.com',
#             password='TestP@ssw0rd', # Hash the password!
#             is_active=True,
#             is_email_verified=True, # Use is_email_verified
#             auth_provider='email'  # Add auth_provider
#         )
#         self.user_id = self.test_user.id

#         # Cache user data to simulate a valid session
#         cache.set(f"id_{self.user_id}", self.user_id, timeout=60)
#         cache.set(f"email_{self.user_id}", 'test@example.com', timeout=600)
#         cache.set(f"password_{self.user_id}", 'TestP@ssw0rd', timeout=600)

#         self.client.force_login(self.test_user) # Log in the client for consistent testing

#     def tearDown(self):
#         cache.clear()  # Clear cache after each test

#     @patch('auth_api.views.create_otp')
#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_success(self, mock_check_user_id, mock_create_otp):
#         """
#         Test successful OTP resend returns 200 OK and the expected data.
#         """
#         mock_check_user_id.return_value = self.test_user # Mock successful check_user_id
#         mock_create_otp.return_value = Response(
#             {'success': 'Email sent', 'otp': True, 'user_id': self.test_user.id},
#             status=status.HTTP_200_OK
#         )

#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data['success'], 'Email sent')
#         self.assertEqual(response.data['otp'], True)
#         self.assertEqual(response.data['user_id'], self.user_id)

#     def test_resend_otp_missing_user_id(self):
#         """
#         Test that missing user_id returns 400 Bad Request.
#         """
#         data = {}  # Missing user_id
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)

#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_invalid_user_id(self, mock_check_user_id):
#         """
#         Test that invalid user_id returns 400 Bad Request.
#         """
#         mock_check_user_id.return_value = Response({"error": "Invalid Session"}, status=status.HTTP_400_BAD_REQUEST) # Mock an invalid user ID error

#         data = {'user_id': 999}  # Nonexistent user_id
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid Session') # Specific error check

#     def test_resend_otp_expired_session(self):
#         """
#         Test that an expired session returns 400 Bad Request.
#         """
#         # Clear cache to simulate expired session
#         cache.clear()

#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertIn("Session expired. Please login again.", response.data['error'])

#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_check_user_id_failure(self, mock_check_user_id):
#         """
#         Test that if check_user_id fails, a 400 Bad Request is returned.
#         """
#         mock_check_user_id.return_value = Response({"error": "Account is deactivated. Contact your admin"}, status=status.HTTP_400_BAD_REQUEST)

#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertIn("Account is deactivated. Contact your admin", response.data['error'])

#     @patch('auth_api.views.create_otp')
#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_create_otp_failure(self, mock_check_user_id, mock_create_otp):
#         """
#         Test that a failure during OTP creation returns 400 Bad Request.
#         """
#         mock_check_user_id.return_value = self.test_user  # Ensure check_user_id succeeds
#         mock_create_otp.return_value = Response({"error": "Something went wrong, could not send OTP. Try again", "otp": False}, status=status.HTTP_400_BAD_REQUEST)

#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Something went wrong, could not send OTP. Try again")

#     @patch('auth_api.views.create_otp')
#     def test_resend_otp_internal_server_error(self, mock_create_otp):
#         """
#         Test for a generic internal server error within the view.
#         """
#         # Simulate an error condition within the view's post method.
#         mock_create_otp.side_effect = Exception("Simulated Internal Server Error")
        
#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertIn("Simulated Internal Server Error", response.data['error']) # Validate error message

#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_throttled(self, mock_check_user_id):
#         """
#         Test that the resend OTP view is throttled after exceeding the rate limit.
#         """
#         mock_check_user_id.return_value = self.test_user

#         data = {'user_id': self.user_id}

#         # ** Crucial: Seed the cache for the throttle to work
#         cache.set(f"id_{self.test_user.id}", self.test_user.id, timeout=60)

#         # Make the first request (should succeed)
#         response1 = self.client.post(self.url, data, format='json')
#         self.assertEqual(response1.status_code, status.HTTP_200_OK)

#         # Make the second request immediately (should be throttled)
#         response2 = self.client.post(self.url, data, format='json')
#         self.assertEqual(response2.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#         self.assertIn('detail', response2.data)

#     @patch('auth_api.views.check_user_id')
#     def test_resend_otp_invalid_cache_data(self, mock_check_user_id):
#         """
#         Test that an expired session due to missing cache data returns 400 Bad Request.
#         """
#         mock_check_user_id.return_value = self.test_user

#         # Clear only email and password, leave id to pass check_throttles
#         cache.delete(f"email_{self.user_id}")
#         cache.delete(f"password_{self.user_id}")

#         data = {'user_id': self.user_id}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertIn("Session expired. Please login again.", response.data['error'])

# class TokenViewTests(APITestCase):
#     """Test the TokenView"""
#     # Part of it which uses check_user_validity is already tested in TokenViewTests

#     def setUp(self):
#         self.url = TOKEN_USER_URL  # Assuming you named your URL 'token_obtain_pair' (or whatever your token URL is)
#         self.test_user = create_user(
#             email='test@example.com',
#             password='TestP@ssw0rd', # Hash the password!
#             is_active=True,
#             is_email_verified=True, # Use is_email_verified
#             auth_provider='email'  # Add auth_provider
#         )
#         self.user_id = self.test_user.id

#         # Cache user data to simulate a valid session and OTP
#         self.otp = generate_otp() # Generate an OTP
#         cache.set(f"id_{self.user_id}", self.user_id, timeout=60)
#         cache.set(f"otp_{self.user_id}", self.otp, timeout=600)
#         cache.set(f"email_{self.user_id}", 'test@example.com', timeout=600)
#         cache.set(f"password_{self.user_id}", 'TestP@ssw0rd', timeout=600)
#         cache.set(f"otp_{self.user_id}", self.otp, timeout=600) # Cache otp

#         self.client.force_login(self.test_user)

#     def tearDown(self):
#         cache.clear()

#     @patch('auth_api.views.check_user_id')
#     def test_token_generation_success(self, mock_check_user_id):
#         """
#         Test successful token generation after OTP verification.
#         """
#         mock_check_user_id.return_value = self.test_user  # Mock check_user_id success

#         data = {
#             'user_id': self.user_id,
#             'otp': f"{self.otp}", # Provide the OTP that's stored in the cache
#         }

#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn('access_token_expiry', response.data)
#         self.assertIn('access_token', response.data)
#         self.assertIn('refresh_token', response.data)
#         self.assertIn('user_role', response.data)
#         self.assertIn('user_id', response.data)

#     def test_token_generation_missing_user_id(self):
#         """
#         Test that missing user_id returns 400 Bad Request.
#         """
#         data = {'otp': '123456'}  # Missing user_id
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual("Session expired. Please login again.", response.data['error'])

#     def test_token_generation_invalid_user_id(self):
#         """
#         Test that invalid user_id returns 400 Bad Request.
#         """
#         data = {'user_id': 999999999, 'otp': '123456'}  # Nonexistent user_id
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid Session') # Specific error check
        
#     def test_token_generation_invalid_str_user_id(self):
#         """
#         Test that invalid user_id returns 400 Bad Request.
#         """
#         data = {'user_id': "some", 'otp': '123456'}  # Nonexistent user_id
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], 'Invalid Session') # Specific error check

#     def test_token_generation_expired_session(self):
#         """
#         Test that an expired session returns 400 Bad Request.
#         """
#         cache.clear() # Simulate an expired session by clearing the cache

#         data = {'user_id': self.user_id, 'otp': '123456'}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertIn("Session expired. Please login again.", response.data['error'])

#     def test_token_generation_missing_otp(self):
#         """
#         Test that missing OTP returns 400 Bad Request.
#         """
#         data = {'user_id': self.user_id}  # Missing otp
#         response = self.client.post(self.url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Invalid OTP")

#     def test_token_generation_invalid_otp(self):
#         """
#         Test that invalid OTP returns 400 Bad Request.
#         """
#         data = {'user_id': self.user_id, 'otp': 'wrongotp'}
#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('error', response.data)
#         self.assertEqual(response.data['error'], "Invalid OTP")

#     @patch('auth_api.views.check_user_id')  # Patch check_user_id to simulate failure
#     def test_token_generation_internal_server_error(self, mock_check_user_id):
#         """
#         Test that an exception in token generation is caught by TokenView and returns a 500 error.
#         """
#         # Simulate an exception being raised in check_user_id.
#         mock_check_user_id.side_effect = Exception("Simulated Internal Server Error")

#         data = {'user_id': self.user_id, 'otp': '123456'}

#         response = self.client.post(self.url, data, format='json')

#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn('error', response.data)
#         self.assertIn("Simulated Internal Server Error", response.data['error'])
        
# class RefreshTokenViewTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.refresh_url = TOKEN_REFRESH_URL # Assuming you named your URL 'token_refresh'

#         # Create a user for testing
#         self.email = "test@example.com"
#         self.password = "Test@123"
#         self.user = create_user(email=self.email, password=self.password)
        
#         self.admin_group, _ = Group.objects.get_or_create(name="Admin")
#         self.superuser_group, _ = Group.objects.get_or_create(name="Superuser")

#         # Generate initial refresh and access tokens for the user
#         self.refresh = RefreshToken.for_user(self.user)
#         self.access = self.refresh.access_token
#         self.refresh_token = str(self.refresh)
#         self.access_token = str(self.access)
        
#     def generate_expired_refresh_token(self):
#         """Manually generate an expired refresh token."""
#         refresh = RefreshToken.for_user(self.user)
#         refresh.payload["exp"] = now() - timedelta(days=1)  # Set expiry in the past
#         return str(refresh)

#     def test_successful_token_refresh(self):
#         """Test successful refresh token exchange."""
#         data = {"refresh": self.refresh_token}
#         response = self.client.post(self.refresh_url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access_token", response.data)
#         self.assertIn("refresh_token", response.data)
#         self.assertIn("user_role", response.data)
#         self.assertIn("user_id", response.data)
#         self.assertIn("access_token_expiry", response.data)

#         self.assertEqual(response.data["user_id"], self.user.id)
#         self.assertEqual(response.data["user_role"], "Default")  # Verify the user role

#     def test_successful_token_refresh_admin_role(self):
#         """Test successful refresh token exchange when user is in Admin group."""
#         # Assign user to 'Admin' group and remove from 'Default'
#         self.user.groups.clear()  # Remove from all groups
#         self.user.groups.add(self.admin_group)

#         # Generate new tokens after group change
#         refresh = RefreshToken.for_user(self.user)
#         refresh_token = str(refresh)

#         data = {"refresh": refresh_token}
#         response = self.client.post(self.refresh_url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["user_role"], "Admin")

#     def test_successful_token_refresh_superuser_role(self):
#         """Test successful refresh token exchange when user is in Superuser group."""
#         # Assign user to 'Superuser' group and remove from other groups
#         self.user.groups.clear()
#         self.user.groups.add(self.superuser_group)

#         # Generate new tokens after group change
#         refresh = RefreshToken.for_user(self.user)
#         refresh_token = str(refresh)

#         data = {"refresh": refresh_token}
#         response = self.client.post(self.refresh_url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["user_role"], "Superuser")

#     def test_token_refresh_no_group(self):
#         """Test refresh token exchange when user is not in any group."""
#         # Remove user from all groups
#         self.user.groups.clear()

#         # Generate new tokens after group change
#         refresh = RefreshToken.for_user(self.user)
#         refresh_token = str(refresh)

#         data = {"refresh": refresh_token}
#         response = self.client.post(self.refresh_url, data, format="json")

#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(response.data["user_role"], "UnAuthorized")

#     def test_missing_refresh_token(self):
#         """Test request with missing refresh token."""
#         response = self.client.post(self.refresh_url, {}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)

#     def test_invalid_refresh_token(self):
#         """Test request with an invalid refresh token."""
#         data = {"refresh": "invalid_refresh_token"}
#         response = self.client.post(self.refresh_url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) # Or 401 depending on your exact error handling
#         self.assertIn("error", response.data)

#     def test_expired_refresh_token(self):
#         """Test request with an expired refresh token."""
#         expired_token = self.generate_expired_refresh_token()
#         data = {"refresh": expired_token}
        
#         response = self.client.post(self.refresh_url, data, format="json")

#         # Since SimpleJWT raises `TokenError`, it should return 401 Unauthorized
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertIn("error", response.data)

#     def test_blacklisted_refresh_token(self):
#         """Test that a blacklisted refresh token is rejected."""

#         # Ensure the refresh token is saved in the `OutstandingToken` table
#         outstanding_token = OutstandingToken.objects.get(token=str(self.refresh_token))

#         # Blacklist the token
#         BlacklistedToken.objects.create(token=outstanding_token)

#         data = {"refresh": str(self.refresh_token)}
#         response = self.client.post(self.refresh_url, data, format="json")

#         # A blacklisted token should return 401 Unauthorized
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
#         self.assertIn("error", response.data)

#     def test_user_not_found(self):
#         """Test the case where the user associated with the token doesn't exist."""
#         # Generate a valid token for a non-existent user ID
#         refresh = RefreshToken()
#         refresh['user_id'] = 9999  # Non-existent user ID
#         refresh_token = str(refresh)

#         data = {"refresh": refresh_token}
#         response = self.client.post(self.refresh_url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)  # Or 401
#         self.assertIn("error", response.data)

# class EmailVerifyViewTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = VERIFY_EMAIL_URL
#         self.valid_email = "test@example.com"
#         self.password = "Test@123"
#         # Create a user with auth_provider 'email' that is not yet verified.
#         self.user = create_user(
#             email=self.valid_email,
#             password=self.password,
#             auth_provider='email',
#             is_email_verified=False,
#             is_active=False
#         )
    
#     def tearDown(self):
#         cache.clear()

#     # ─── GET METHOD TESTS ─────────────────────────────────────────────────────────

#     @patch('auth_api.views.check_token_validity')
#     def test_email_verify_get_success(self, mock_check_token_validity):
#         """
#         When the token is valid and a matching user exists,
#         the GET request should verify the email and return success.
#         """
#         # Simulate a valid token check by returning the email.
#         mock_check_token_validity.return_value = self.valid_email

#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': 1234567890})
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("success", response.data)
#         self.assertEqual(response.data["success"], "Email verified successfully")
#         # Check that the user record is updated.
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.is_active)
#         self.assertTrue(self.user.is_email_verified)

#     @patch('auth_api.views.check_token_validity')
#     def test_email_verify_get_invalid_user(self, mock_check_token_validity):
#         """
#         If check_token_validity returns an email for which no user exists,
#         the view should return a 400 error with "Invalid credentials".
#         """
#         non_existing_email = "nonexistent@example.com"
#         mock_check_token_validity.return_value = non_existing_email

#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': 9999999999})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid credentials")

#     @patch('auth_api.views.check_token_validity')
#     def test_email_verify_get_token_returns_response(self, mock_check_token_validity):
#         """
#         If check_token_validity returns a Response (indicating an error),
#         the view should immediately return that Response.
#         """
#         error_response = Response({"error": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
#         mock_check_token_validity.return_value = error_response

#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': 9999999999})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid or expired token")

#     # ─── Tests That Let check_token_validity Run Its Logic ─────────────────────

#     def test_email_verify_get_missing_token(self):
#         """
#         If no token is provided, check_token_validity should return an error.
#         """
#         response = self.client.get(self.url, {'expiry': 9999999999})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Missing verification link.")

#     def test_email_verify_get_missing_expiry(self):
#         """
#         If no expiry is provided, check_token_validity should return an error.
#         """
#         response = self.client.get(self.url, {'token': 'dummy'})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Missing verification link.")

#     def test_email_verify_get_expired_link(self):
#         """
#         If the expiry time is in the past, check_token_validity should return an error.
#         """
#         past_timestamp = int((now() - timedelta(seconds=10)).timestamp())
#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': past_timestamp})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "The verification link has expired.")

#     def test_email_verify_get_invalid_token_valueerror(self):
#         """
#         If EmailLink.verify_link raises a ValueError (e.g., invalid signature),
#         check_token_validity should catch it and return an error response.
#         """
#         with patch('auth_api.views.EmailLink.verify_link', side_effect=ValueError("Invalid verification link")):
#             future_timestamp = int((now() + timedelta(seconds=60)).timestamp())
#             response = self.client.get(self.url, {'token': 'dummy', 'expiry': future_timestamp})
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertIn("error", response.data)
#             self.assertEqual(response.data["error"], "Invalid verification link")

#     @patch('auth_api.views.check_token_validity')
#     def test_email_verify_get_exception(self, mock_check_token_validity):
#         """
#         If check_token_validity raises an exception, the view should return a 500 error.
#         """
#         mock_check_token_validity.side_effect = Exception("Simulated exception")
#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': 1234567890})
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Simulated exception")

#     # ─── POST METHOD TESTS ─────────────────────────────────────────────────────────

#     def test_email_verify_post_success(self):
#         """
#         When a valid email is provided for a user who is not yet verified,
#         and EmailLink.send_email_link returns True,
#         the view should send the verification link and return a 201 response.
#         """
#         with patch('auth_api.views.EmailLink.send_email_link', return_value=True) as mock_send_email:
#             data = {"email": self.valid_email}
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertIn("success", response.data)
#             self.assertEqual(
#                 response.data["success"],
#                 "Verification link sent. Please verify your email to activate your account."
#             )
#             # Verify that the email is cached.
#             cached_email = cache.get(f"email_{self.valid_email}")
#             self.assertEqual(cached_email, self.valid_email)

#     def test_email_verify_post_user_not_found(self):
#         """
#         If the provided email does not match any user,
#         the view should return a 400 error with "Invalid credentials".
#         """
#         data = {"email": "unknown@example.com"}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid credentials")

#     def test_email_verify_post_wrong_auth_provider(self):
#         """
#         If the user exists but was created with a different auth provider,
#         the view should return a 400 error indicating that the process cannot be used.
#         """
#         # Create a user with a different auth provider.
#         other_email = "other@example.com"
#         user2 = create_user(
#             email=other_email,
#             password="Test@123",
#             auth_provider="google",
#             is_email_verified=False
#         )
#         data = {"email": other_email}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         expected_error = f"This process cannot be used, as user is created using {user2.auth_provider}"
#         self.assertEqual(response.data["error"], expected_error)

#     def test_email_verify_post_already_verified(self):
#         """
#         If the user is already verified, the view should return a 400 error.
#         """
#         # Create a user that is already verified.
#         verified_email = "verified@example.com"
#         create_user(
#             email=verified_email,
#             password="Test@123",
#             auth_provider="email",
#             is_email_verified=True
#         )
#         data = {"email": verified_email}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Email already verified")

#     def test_email_verify_post_email_link_fail(self):
#         """
#         If EmailLink.send_email_link fails (returns False),
#         the view should return a 500 error.
#         """
#         with patch('auth_api.views.EmailLink.send_email_link', return_value=False):
#             data = {"email": self.valid_email}
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertEqual(response.data["error"], "Failed to send email verification link.")
            
#     def test_email_verify_post_throttled(self):
#         """
#         Test that when throttle conditions are met, the view returns a 429 error.
#         We simulate this by:
#           1. Caching the email (so that `cached_email` is truthy).
#           2. Patching `check_throttle_duration` to return a non-empty value.
#           3. Patching `start_throttle` to raise a Throttled exception.
#         """
#         # Pre-populate the cache so that the view sees a cached email.
#         cache.set(f"email_{self.valid_email}", self.valid_email, timeout=60)
#         data = {"email": self.valid_email}
#         # Patch both throttle-related functions.
#         with patch('auth_api.views.check_throttle_duration', return_value=10):
#             with patch('auth_api.views.start_throttle', side_effect=Throttled(detail="Request was throttled. Expected available in 10 seconds.")):
#                 response = self.client.post(self.url, data, format="json")
#                 self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#                 self.assertIn("Request was throttled", response.data.get("detail", ""))

#     def test_email_verify_post_exception(self):
#         """
#         If an exception occurs during processing the POST request,
#         the view should return a 500 error with the exception message.
#         """
#         with patch('auth_api.views.get_user_model') as mock_get_user_model:
#             mock_get_user_model.side_effect = Exception("Simulated exception in post")
#             data = {"email": self.valid_email}
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertEqual(response.data["error"], "Simulated exception in post")

# class PublicPhoneVerifyViewTests(APITestCase):
#     def setUp(self):
#         self.url = VERIFY_PHONE_URL
#         self.client = APIClient()
        
#     def test_phone_verify_post_unauthenticated(self):
#         """
#         Test that an unauthenticated request to send an OTP returns 401 Unauthorized.
#         """
#         # Do not authenticate the client.
#         response = self.client.post(self.url, {}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
#     def test_phone_verify_patch_unauthenticated(self):
#         """
#         Test that an unauthenticated request to verify an OTP returns 401 Unauthorized.
#         """
#         data = {"otp": "0"}
#         response = self.client.patch(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

# class PrivatePhoneVerifyViewTests(APITestCase):
#     def setUp(self):
#         self.url = VERIFY_PHONE_URL
#         # Create a test user with a phone_number and not yet verified.
#         self.user = create_user(
#             email="test@example.com",
#             password="Test@123",
#             auth_provider="email",
#             is_phone_verified=False,
#         )
#         # Set a phone number for the user. (Assume your user model has a phone_number field.)
#         self.user.phone_number = "+8801912345678"
#         self.user.save()
#         self.client = APIClient()
#         self.client.force_authenticate(user=self.user)

#     def tearDown(self):
#         cache.clear()

#     def test_phone_verify_post_success(self):
#         """
#         Test that a logged‑in user receives an OTP successfully.
#         The view should return a 200 response with success message.
#         """
#         response = self.client.post(self.url, {}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("success", response.data)
#         self.assertEqual(response.data["success"], "OTP sent successfully")
#         # Verify that an OTP was stored in the cache.
#         otp = cache.get(f"phone_otp_{self.user.phone_number}")
#         self.assertIsNotNone(otp)

#     def test_phone_verify_post_fail(self):
#         """
#         If PhoneOtp.send_otp returns False, the view should return a 400 error.
#         """
#         with patch('auth_api.views.PhoneOtp.send_otp', return_value=False):
#             response = self.client.post(self.url, {}, format="json")
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertIn("error", response.data)
#             self.assertEqual(response.data["error"], "Something went wrong, could not send OTP. Try again")

#     def test_phone_verify_post_exception(self):
#         """
#         Test that if an exception occurs during OTP sending, the view returns a 500 error.
#         """
#         with patch('auth_api.views.PhoneOtp.send_otp', side_effect=Exception("Simulated exception")):
#             response = self.client.post(self.url, {}, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertIn("error", response.data)
#             self.assertEqual(response.data["error"], "Simulated exception")

#     def test_phone_verify_post_throttled(self):
#         """
#         Test that if throttle conditions are met, the view returns a 429 error.
#         We simulate throttling by patching the throttle helpers.
#         """
#         with patch('auth_api.views.check_throttle_duration', return_value=10):
#             with patch('auth_api.views.start_throttle', side_effect=Throttled(detail="Request was throttled. Expected available in 10 seconds.")):
#                 response = self.client.post(self.url, {}, format="json")
#                 self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#                 # DRF usually returns the throttling message under the "detail" key.
#                 self.assertIn("Request was throttled", response.data.get("detail", ""))

#     # ─── Tests for PATCH method (Verifying OTP) ──────────────────────────────

#     def test_phone_verify_patch_success(self):
#         """
#         Test that a logged‑in user can successfully verify their phone number when providing the correct OTP.
#         """
#         # As per PhoneOtp.send_otp, the OTP is set to 000000 (which is 0 in Python).
#         cache.set(f"phone_otp_{self.user.phone_number}", 0, 600)
#         data = {"otp": "0"}
#         response = self.client.patch(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("success", response.data)
#         self.assertEqual(response.data["success"], "Phone verified successfully")
#         # Verify that the user's phone is now marked as verified.
#         self.user.refresh_from_db()
#         self.assertTrue(self.user.is_phone_verified)
#         # The OTP should also be removed from the cache.
#         otp = cache.get(f"phone_otp_{self.user.phone_number}")
#         self.assertIsNone(otp)

#     def test_phone_verify_patch_missing_otp(self):
#         """
#         Test that if no OTP is provided in the PATCH request, the view returns a 400 error.
#         """
#         data = {}  # OTP is missing.
#         response = self.client.patch(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "OTP is required")

#     def test_phone_verify_patch_invalid_otp(self):
#         """
#         Test that if an incorrect OTP is provided, the view returns a 400 error with "Invalid OTP".
#         """
#         # Set the correct OTP in cache (which is 0).
#         cache.set(f"phone_otp_{self.user.phone_number}", 0, 600)
#         data = {"otp": "123456"}  # An incorrect OTP.
#         response = self.client.patch(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Invalid OTP")

#     def test_phone_verify_patch_exception(self):
#         """
#         Test that if an exception occurs during OTP verification (e.g. in PhoneOtp.verify_otp),
#         the view returns a 500 error.
#         """
#         with patch('auth_api.views.PhoneOtp.verify_otp', side_effect=Exception("Simulated exception in verify_otp")):
#             data = {"otp": "0"}
#             response = self.client.patch(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertIn("error", response.data)
#             self.assertEqual(response.data["error"], "Simulated exception in verify_otp")
            
# class PasswordResetViewTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = RESET_PASSWORD_URL
#         self.user_model = get_user_model()
#         self.valid_email = "valid@example.com"
#         self.old_password = "OldPassword1!"
#         # Create a valid user for success scenarios.
#         self.user = create_user(
#             email=self.valid_email,
#             password=self.old_password,
#             auth_provider='email',
#             is_email_verified=True,
#             is_active=True
#         )
        
#     def tearDown(self):
#         cache.clear()

#     # ────────────── GET Method Tests ──────────────

#     def test_password_reset_get_missing_parameters(self):
#         """GET without token and expiry should return a missing verification link error."""
#         response = self.client.get(self.url)  # No token, no expiry provided.
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Missing verification link.")

#     def test_password_reset_get_expired_link(self):
#         """GET with an expired expiry should return an error."""
#         past_timestamp = int((now() - timedelta(minutes=1)).timestamp())
#         response = self.client.get(self.url, {'token': 'dummy', 'expiry': past_timestamp})
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "The verification link has expired.")

#     def test_password_reset_get_invalid_link(self):
#         """GET with an invalid token should return an error (simulate EmailLink.verify_link failure)."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         with patch('auth_api.views.EmailLink.verify_link', side_effect=ValueError("Invalid verification link.")):
#             response = self.client.get(self.url, {'token': 'dummy', 'expiry': future_timestamp})
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual(response.data["error"], "Invalid verification link.")

#     def test_password_reset_get_success(self):
#         """GET with valid token and expiry should return a success message."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         # Patch EmailLink.verify_link to return our valid email.
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.get(self.url, {'token': 'validtoken', 'expiry': future_timestamp})
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self.assertEqual(response.data["success"], "Password verification link ok")

#     def test_password_reset_get_exception(self):
#         """GET should return a 500 error if an unexpected exception occurs."""
#         with patch('auth_api.views.check_token_validity', side_effect=Exception("GET exception")):
#             response = self.client.get(self.url, {'token': 'dummy', 'expiry': '9999999999'})
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertEqual(response.data["error"], "GET exception")

#     # ────────────── POST Method Tests ──────────────

#     def test_password_reset_post_invalid_user(self):
#         """POST with an email that does not exist should return 'Invalid credentials'."""
#         data = {"email": "nonexistent@example.com"}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Invalid credentials")

#     def test_password_reset_post_wrong_auth_provider(self):
#         """POST with a user created via a non-email provider should return an error."""
#         # Create a user with a different auth provider.
#         user2 = create_user(
#             email="google@example.com",
#             password="Password1!",
#             auth_provider="google",
#             is_email_verified=True,
#             is_active=True
#         )
#         data = {"email": "google@example.com"}
#         response = self.client.post(self.url, data, format="json")
#         expected_error = f"This process cannot be used, as user is created using {user2.auth_provider}"
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], expected_error)

#     def test_password_reset_post_not_verified(self):
#         """POST with a user whose email is not verified should return an error."""
#         user3 = create_user(
#             email="notverified@example.com",
#             password="Password1!",
#             auth_provider="email",
#             is_email_verified=False,
#             is_active=True
#         )
#         data = {"email": "notverified@example.com"}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Email is not verified. You must verify your email first")

#     def test_password_reset_post_inactive(self):
#         """POST with an inactive user should return an error."""
#         user4 = create_user(
#             email="inactive@example.com",
#             password="Password1!",
#             auth_provider="email",
#             is_email_verified=True,
#             is_active=False
#         )
#         data = {"email": "inactive@example.com"}
#         response = self.client.post(self.url, data, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Account is deactivated. Contact your admin")

#     def test_password_reset_post_email_link_fail(self):
#         """POST should return a 500 error if sending the password reset link fails."""
#         data = {"email": self.valid_email}
#         with patch('auth_api.views.EmailLink.send_password_reset_link', return_value=False):
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertEqual(response.data["error"], "Failed to send password reset link.")

#     def test_password_reset_post_success(self):
#         """POST with valid input should send the reset link and return a 201 response."""
#         data = {"email": self.valid_email}
#         with patch('auth_api.views.EmailLink.send_password_reset_link', return_value=True):
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#             self.assertEqual(
#                 response.data["success"],
#                 "Password reset link sent. Please check your email to reset your password."
#             )
#             # Verify that the email is cached.
#             cached_email = cache.get(f"email_{self.valid_email}")
#             self.assertEqual(cached_email, self.valid_email)

#     def test_password_reset_post_throttled(self):
#         """POST should return 429 when throttling conditions are met."""
#         data = {"email": self.valid_email}
#         # Pre-cache the email so that throttling is triggered.
#         cache.set(f"email_{self.valid_email}", self.valid_email, timeout=60)
#         with patch('auth_api.views.check_throttle_duration', return_value=10):
#             with patch('auth_api.views.start_throttle', side_effect=Throttled(detail="Request was throttled. Expected available in 10 seconds.")):
#                 response = self.client.post(self.url, data, format="json")
#                 self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#                 self.assertIn("Request was throttled", response.data.get("detail", ""))

#     def test_password_reset_post_exception(self):
#         """POST should return a 500 error if an unexpected exception occurs."""
#         with patch('auth_api.views.get_user_model', side_effect=Exception("POST exception")):
#             data = {"email": self.valid_email}
#             response = self.client.post(self.url, data, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertEqual(response.data["error"], "POST exception")

#     # ────────────── PATCH Method Tests ──────────────

#     def test_password_reset_patch_missing_token(self):
#         """PATCH without token in query parameters should return an error."""
#         response = self.client.patch(
#             self.url,
#             {"password": "NewPassword1!", "c_password": "NewPassword1!"},
#             format="json"
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Missing verification link.")

#     def test_password_reset_patch_expired_link(self):
#         """PATCH with an expired link should return an error."""
#         past_timestamp = int((now() - timedelta(minutes=1)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={past_timestamp}"
#         response = self.client.patch(
#             url,
#             {"password": "NewPassword1!", "c_password": "NewPassword1!"},
#             format="json"
#         )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "The verification link has expired.")

#     def test_password_reset_patch_invalid_link(self):
#         """PATCH with an invalid token should return an error (simulate invalid link)."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         with patch('auth_api.views.EmailLink.verify_link', side_effect=ValueError("Invalid verification link.")):
#             response = self.client.patch(
#                 url,
#                 {"password": "NewPassword1!", "c_password": "NewPassword1!"},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual(response.data["error"], "Invalid verification link.")

#     def test_password_reset_patch_invalid_user(self):
#         """PATCH with a token that returns an email not linked to any user should return an error."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         # Simulate a valid token that returns a non-existent email.
#         with patch('auth_api.views.EmailLink.verify_link', return_value="nonexistent@example.com"):
#             response = self.client.patch(
#                 url,
#                 {"password": "NewPassword1!", "c_password": "NewPassword1!"},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual(response.data["error"], "Invalid credentials")

#     def test_password_reset_patch_passwords_do_not_match(self):
#         """PATCH when provided passwords do not match should return an error."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.patch(
#                 url,
#                 {"password": "NewPassword1!", "c_password": "Mismatch1!"},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual(response.data["error"], "Passwords do not match")

#     def test_password_reset_patch_missing_password(self):
#         """
#         Test that if no password is provided in the PATCH request,
#         the serializer raises an error ("Password is required.").
#         """
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.patch(
#                 url,
#                 {},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             # Will raise an error typically handled by frontend before even reaching backend
            
#     def test_password_reset_patch_same_as_old(self):
#         """
#         Test that if the new password is the same as the user's old password,
#         the serializer raises an error ("New password cannot be the same as the old password.").
#         """
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.patch(
#                 url,
#                 {"password": self.old_password, "c_password": self.old_password},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual('New password cannot be the same as the old password.', response.data[0])

#     def test_password_reset_patch_weak_password(self):
#         """
#         Test that if the new password is too weak (e.g. too short),
#         the serializer raises a validation error with details from validate_password.
#         """
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         weak_password = "weak"  # Too short and likely fails other criteria.
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.patch(
#                 url,
#                 {"password": weak_password, "c_password": weak_password},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertEqual("Password must be at least 8 characters long.", response.data['short'])
#             self.assertEqual("Password must contain at least one uppercase letter.", response.data['upper'])
#             self.assertEqual("Password must contain at least one number.", response.data['number'])
#             self.assertEqual("Password must contain at least one special character.", response.data['special'])
#             #Lowercase can also be checked but not necessary as these errors are part of the same group

#     def test_password_reset_patch_success(self):
#         """PATCH with valid data should reset the password successfully."""
#         future_timestamp = int((now() + timedelta(minutes=10)).timestamp())
#         url = f"{self.url}?token=dummy&expiry={future_timestamp}"
#         new_password = "NewPassword1!"
#         with patch('auth_api.views.EmailLink.verify_link', return_value=self.valid_email):
#             response = self.client.patch(
#                 url,
#                 {"password": new_password, "c_password": new_password},
#                 format="json"
#             )
#             self.assertEqual(response.status_code, status.HTTP_200_OK)
#             self.assertEqual(response.data["success"], "Password reset successful.")
#             # Verify that the user's password was updated.
#             self.user.refresh_from_db()
#             self.assertTrue(self.user.check_password(new_password))

# class PublicUserApiTests(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.url = USER_URL
        
#     def tearDown(self):
#         cache.clear()

#     def test_create_user_success(self):
#         """Test creating a user successfully."""
#         payload = {
#             'email': 'test@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         user = get_user_model().objects.get(email=payload['email'])
#         self.assertTrue(user.check_password(payload['password']))
#         self.assertNotIn('password', res.data)
#         # Expect default profile image if none provided.
#         default_image_path = 'profile_images/default_profile.jpg'
#         self.assertEqual(user.profile_img.name, default_image_path)

#     def test_create_user_missing_c_password(self):
#         """Test that creating a user without c_password returns an error."""
#         payload = {
#             'email': 'test2@example.com',
#             'password': 'Django@123',
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(res.data['error'], "Please confirm your password.")

#     def test_create_user_passwords_do_not_match(self):
#         """Test that mismatched password and c_password return an error."""
#         payload = {
#             'email': 'test3@example.com',
#             'password': 'Django@123',
#             'c_password': 'Mismatch@123',
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(res.data['error'], "Passwords do not match")

#     def test_create_user_forbidden_superuser_field(self):
#         """Test that providing is_superuser in the payload returns a 403 error."""
#         payload = {
#             'email': 'test4@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'is_superuser': True,
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             res.data['error'],
#             "You do not have permission to create a superuser. Contact Developer."
#         )

#     def test_create_user_forbidden_staff_field(self):
#         """Test that providing is_staff (for non-superuser) returns a 403 error."""
#         payload = {
#             'email': 'test5@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'is_staff': True,
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(res.data['error'], "You do not have permission to create an admin user.")

#     def test_create_user_forbidden_profile_img(self):
#         """Test that providing profile_img in create returns a 403 error."""
#         payload = {
#             'email': 'test6@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'profile_img': "some_image.png"
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(
#             res.data['error'],
#             "Profile Image cannot be updated here. Use the Upload Image Action."
#         )

#     def test_create_user_forbidden_fields(self):
#         """Test that including forbidden fields (slug, is_email_verified, etc.) returns a 403 error."""
#         payload = {
#             'email': 'test7@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'slug': 'some-slug'
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#         self.assertEqual(res.data['error'], "Forbidden fields cannot be updated.")

#     def test_create_user_with_invalid_email(self):
#         payload = {
#             'email': 'x',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Enter a valid email address", json.dumps(res.data['email']))
    
#     def test_create_user_with_already_created_email_username(self):
#         payload = {
#             'email': 'test1@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'username': 'test1@example.com',
#         }
#         with patch('auth_api.views.check_throttle_duration', return_value=None):
#             old_res = self.client.post(self.url, payload, format='json')
#             self.assertEqual(old_res.status_code, status.HTTP_201_CREATED)
#             new_res = self.client.post(self.url, payload, format='json')
#             self.assertEqual(new_res.status_code, status.HTTP_400_BAD_REQUEST)
#             self.assertIn("user with this email already exists.", json.dumps(new_res.data['email']))
#             self.assertIn("user with this username already exists.", json.dumps(new_res.data['username']))
            
#     def test_create_user_with_invalid_phone(self):
#         payload = {
#             'email': 'test9@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'phone_number': '12334455667'
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("The phone number entered is not valid.", json.dumps(res.data['phone_number']))
        
#     def test_create_user_short_username(self):
#         """Test that a username shorter than 6 characters returns a serializer error."""
#         payload = {
#             'email': 'test10@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'username': 'usr'
#         }
#         res = self.client.post(self.url, payload, format='json')
#         self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("Username must be at least 6 characters long", json.dumps(res.data['username']))

#     def test_password_reset_patch_weak_password(self):
#         """
#         Test that if the new password is too weak (e.g. too short),
#         the serializer raises a validation error with details from validate_password.
#         """
#         payload = {
#             'email': 'test11@example.com',
#             'password': 'weak',
#             'c_password': 'weak',
#         }
#         response = self.client.post(self.url, payload, format='json')
#         pass_error = response.data['password']
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual("Password must be at least 8 characters long.", pass_error['short'])
#         self.assertEqual("Password must contain at least one uppercase letter.", pass_error['upper'])
#         self.assertEqual("Password must contain at least one number.", pass_error['number'])
#         self.assertEqual("Password must contain at least one special character.", pass_error['special'])
#         #Lowercase can also be checked but not necessary as these errors are part of the same group

#     def test_create_user_throttled(self):
#         """Simulate throttling on user creation when the email is already cached."""
#         payload = {
#             'email': 'test12@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#         }
#         # Pre-populate the cache for this email.
#         cache.set(f"email_{payload['email']}", payload['email'], timeout=60)
#         with patch('auth_api.views.start_throttle', side_effect=Throttled(detail="Request was throttled. Expected available in 10 seconds.")):
#             with patch('auth_api.views.check_throttle_duration', return_value=10):
#                 res = self.client.post(self.url, payload, format='json')
#                 self.assertEqual(res.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
#                 self.assertIn("Request was throttled", res.data.get("detail", ""))
                
#     def test_create_user_email_link_failure(self):
#         """
#         Test that if EmailLink.send_email_link returns False,
#         the user creation view returns a 500 error with the appropriate error message.
#         """
#         payload = {
#             'email': 'testfailure@example.com',
#             'password': 'Django@123',
#             'c_password': 'Django@123',
#             'username': 'testuserfailure'
#         }
#         # Patch EmailLink.send_email_link to simulate failure
#         with patch('auth_api.views.EmailLink.send_email_link', return_value=False):
#             res = self.client.post(USER_URL, payload, format='json')
        
#         self.assertEqual(res.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(res.data["error"], "Failed to send email verification link.")

#     def test_list_users_unauthorized(self):
#         """Test that listing users without authentication returns 401 Unauthorized."""
#         res = self.client.get(USER_URL, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_retrieve_user_unauthorized(self):
#         """Test that retrieving a user without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth@example.com",
#             password="Password@123",
#             username="unauthuser"
#         )
#         url = detail_url(user.id)
#         res = self.client.get(url, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_update_user_unauthorized(self):
#         """Test that updating a user without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth2@example.com",
#             password="Password@123",
#             username="unauthuser2"
#         )
#         url = detail_url(user.id)
#         res = self.client.patch(url, {"first_name": "NewName"}, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_destroy_user_unauthorized(self):
#         """Test that deleting a user without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth3@example.com",
#             password="Password@123",
#             username="unauthuser3"
#         )
#         url = detail_url(user.id)
#         res = self.client.delete(url, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_upload_image_unauthorized(self):
#         """Test that uploading an image without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth4@example.com",
#             password="Password@123",
#             username="unauthuser4"
#         )
#         # Assuming the upload image endpoint is defined as /api/users/<id>/upload-image/
#         url = image_upload_url(user.id)
#         res = self.client.patch(url, {}, format="multipart")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_deactivate_user_unauthorized(self):
#         """Test that deactivating a user without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth5@example.com",
#             password="Password@123",
#             username="unauthuser5"
#         )
#         url = deactivate_user_url(user.id)
#         res = self.client.patch(url, {}, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

#     def test_activate_user_unauthorized(self):
#         """Test that activating a user without authentication returns 401 Unauthorized."""
#         user = create_user(
#             email="unauth6@example.com",
#             password="Password@123",
#             username="unauthuser6"
#         )
#         url = activate_user_url(user.id)
#         res = self.client.patch(url, {}, format="json")
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateUserApiTests(APITestCase):
    """Test user API requests that require authentication."""

    def setUp(self):
        """Environment setup"""
        self.user = create_user(
            email='test@example.com',
            password='Django@123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.url = detail_url(self.user.id)

    #------------------GET------------------#

    # def test_list_users(self):
    #     """Test retrieving a paginated list of users."""
    #     res = self.client.get(USER_URL)
        
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn('results', res.data)
    #     self.assertIn('count', res.data)
    #     self.assertIn('total_pages', res.data)

    # def test_retrieve_user(self):
    #     """Test retrieving a single user by ID."""
    #     res = self.client.get(self.url)
        
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertEqual(res.data['email'], self.user.email)

    # def test_filter_users_by_search(self):
    #     """Test filtering users by email or username."""
    #     response = self.client.get(USER_URL, {'search': 'test'})
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(len(response.data['results']) > 0)

    # def test_filter_users_by_group(self):
    #     """Test filtering users by group name."""
    #     response = self.client.get(USER_URL, {'group': 'admin'})
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertTrue(len(response.data['results']) == 0)

    # def test_pagination(self):
    #     """Test that user list pagination works."""
    #     response = self.client.get(USER_URL, {'page': 1, 'page_size': 2})
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('next', response.data)
    #     self.assertIn('previous', response.data)
        
    #------------------CREATE------------------#
    
    # def test_create_admin_success(self):
    #     """Test creating an admin user successfully."""
    #     superuser = get_user_model().objects.create_superuser(
    #         email='admin@example.com',
    #         password='Admin@123',
    #     )
    #     self.client.force_authenticate(user=superuser)
    #     payload = {
    #         'email': 'test1@example.com',
    #         'password': 'Django@123',
    #         'c_password': 'Django@123',
    #         'is_staff': True
    #     }
    #     res = self.client.post(USER_URL, payload, format='json')
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     user = get_user_model().objects.get(email=payload['email'])
    #     self.assertTrue(user.check_password(payload['password']))
    #     self.assertTrue(user.is_staff)
    #     self.assertNotIn('password', res.data)
        
    #------------------UPDATE------------------#
        
    # def test_successful_update(self):
    #     """Test updating user's own profile successfully."""
    #     payload = {"first_name": "John", "last_name": "Doe"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertEqual(response.data["success"], "User profile updated successfully.")
    
    # def test_superuser_can_update_any_user(self):
    #     """Test that a superuser can update any user's profile."""
    #     superuser = get_user_model().objects.create_superuser(
    #         email='admin@example.com',
    #         password='Admin@123',
    #     )
    #     self.client.force_authenticate(user=superuser)
    #     payload = {"first_name": "Updated"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    # def test_email_cannot_be_updated(self):
    #     """Test that forbidden fields cannot be updated."""
    #     payload = {"email": "new@example.com"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("You cannot update the email field.", response.data["error"])
    
    # def test_profile_img_cannot_be_updated(self):
    #     """Test that profile image cannot be updated through this endpoint."""
    #     payload = {"profile_img": "new_image.jpg"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("Profile Image cannot be updated here.", response.data["error"])
    
    # def test_password_cannot_be_updated(self):
    #     """Test that password cannot be updated without a verification link."""
    #     payload = {"password": "NewPass@123"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("Password reset cannot be done without verification link.", response.data["error"])
        
    # def test_forbidden_field_update(self):
    #     """Test that forbidden fields cannot be updated."""
    #     payload = {"is_staff": True}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("Forbidden fields cannot be updated.", response.data["error"])
        
    # def test_other_user_cannot_update(self):
    #     """Test that a non-superuser cannot update another user's profile."""
    #     other_user = get_user_model().objects.create_user(
    #         email='other@example.com',
    #         password='Other@123',
    #     )
    #     self.client.force_authenticate(user=other_user)
    #     payload = {"first_name": "Updated"}
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    #     self.assertIn("You do not have permission to update this user.", response.data["error"])
        
    # def test_username_already_exists_validation(self):
    #     """Test username validation errors."""
    #     other_user = get_user_model().objects.create_user(
    #         email='other@example.com',
    #         password='Other@123',
    #         username='abcdefgh'
    #     )
    #     payload = {"username": "abcdefgh"}  # Too short
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("user with this username already exists.", json.dumps(response.data["username"]))
        
    # def test_username_short_validation(self):
    #     """Test username validation errors."""
    #     payload = {"username": "abc"}  # Too short
    #     response = self.client.patch(self.url, payload)
        
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("Username must be at least 6 characters long.", json.dumps(response.data["username"]))
        
    # def test_update_user_invalid_phone_number(self):
    #     """Test that invalid phone numbers are rejected."""
    #     payload = {'phone_number': 'invalid123'}
    #     response = self.client.patch(self.url, payload)
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn("The phone number entered is not valid.", json.dumps(response.data['phone_number']))

    # def test_put_method_not_allowed(self):
    #     """Test that PUT method is not allowed."""
    #     payload = {'first_name': 'Should Fail'}
    #     response = self.client.put(self.url, payload)
    #     self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    #     self.assertIn('error', response.data)
    
    #------------------DELETE------------------#

# class SocialAuthViewTests(APITestCase):
#     def setUp(self):
#         self.url = SOCIAL_LOGIN_URL
#         self.token = "valid_token"
#         self.provider = "google-oauth2"
#         # Create a valid user for success scenarios.
#         self.user = create_user(
#             email="social@example.com",
#             password="DummyPassword1!"
#         )
#         self.user.auth_provider = "google"
#         self.user.save()

#     def get_dummy_backend(self, return_value=None, side_effect=None):
#         """
#         Returns a dummy backend instance with a do_auth() method.
#         If side_effect is provided, calling do_auth() will raise that exception.
#         Otherwise, it returns the value specified by return_value.
#         """
#         DummyBackend = type('DummyBackend', (), {})  # Create a new dummy type.
#         dummy_backend = DummyBackend()
#         if side_effect is not None:
#             def do_auth(token):
#                 raise side_effect
#             dummy_backend.do_auth = do_auth
#         else:
#             dummy_backend.do_auth = lambda token: return_value
#         return dummy_backend

#     def test_missing_token_or_provider(self):
#         """Test that if token or provider is missing, a 400 error is returned."""
#         # Missing token.
#         response = self.client.post(self.url, {"provider": self.provider}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Token and provider are required")
#         # Missing provider.
#         response = self.client.post(self.url, {"token": self.token}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Token and provider are required")

#     def test_backend_returns_response_error(self):
#         """
#         Simulate the social auth pipeline returning a Response error.
#         For example, the pipeline may return a Response if a user with that email
#         already exists with password signup.
#         """
#         error_response = Response(
#             {"error": "User with this email already created using password. Please login using password."},
#             status=status.HTTP_400_BAD_REQUEST
#         )
#         dummy_backend = self.get_dummy_backend(return_value=error_response)
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 response = self.client.post(
#                     self.url, {"token": self.token, "provider": self.provider}, format="json"
#                 )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"],
#                          "User with this email already created using password. Please login using password.")

#     def test_account_deactivated(self):
#         """Simulate backend.do_auth returning a user that is deactivated."""
#         deactivated_user = self.user
#         deactivated_user.is_active = False
#         deactivated_user.save()
#         dummy_backend = self.get_dummy_backend(return_value=deactivated_user)
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 response = self.client.post(
#                     self.url, {"token": self.token, "provider": self.provider}, format="json"
#                 )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Account is deactivated. Contact your admin.")

#     def test_auth_failed_user_not_found(self):
#         """Simulate backend.do_auth returning None (i.e. user not found)."""
#         dummy_backend = self.get_dummy_backend(return_value=None)
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 response = self.client.post(
#                     self.url, {"token": self.token, "provider": self.provider}, format="json"
#                 )
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(response.data["error"], "Authentication failed, user not found.")

#     def test_successful_social_auth(self):
#         """Simulate a successful social authentication returning a valid user."""
#         dummy_backend = self.get_dummy_backend(return_value=self.user)
#         # Patch get_user_role to return a dummy role.
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 with patch('auth_api.views.get_user_role', return_value="User"):
#                     response = self.client.post(
#                         self.url, {"token": self.token, "provider": self.provider}, format="json"
#                     )
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("access_token", response.data)
#         self.assertIn("refresh_token", response.data)
#         self.assertIn("access_token_expiry", response.data)
#         self.assertIn("user_role", response.data)
#         self.assertIn("user_id", response.data)
#         self.assertEqual(response.data["user_role"], "User")
#         self.assertEqual(response.data["user_id"], self.user.id)

#     def test_auth_exception(self):
#         """Simulate that backend.do_auth raises an AuthException."""
#         # Update the side_effect to pass two arguments to AuthException:
#         dummy_backend = self.get_dummy_backend(side_effect=AuthException(self.provider, "Social auth error"))
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 response = self.client.post(
#                     self.url, {"token": self.token, "provider": self.provider}, format="json"
#                 )
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(response.data["error"], "Social auth error")

#     def test_generic_exception(self):
#         """Simulate that a generic exception is raised in the try block."""
#         dummy_backend = self.get_dummy_backend(side_effect=Exception("Generic error"))
#         with patch('auth_api.views.load_strategy', return_value="dummy_strategy"):
#             with patch('auth_api.views.load_backend', return_value=dummy_backend):
#                 response = self.client.post(
#                     self.url, {"token": self.token, "provider": self.provider}, format="json"
#                 )
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertEqual(response.data["error"], "Generic error")

# class LogoutViewTests(APITestCase):
#     def setUp(self):
#         self.url = LOGOUT_URL
#         # Create a test user (adjust required fields as per your user model)
#         self.user = create_user(
#             email="test@example.com",
#             password="TestPassword1!"
#         )
#         # Generate a valid refresh token for the user
#         self.refresh_token = str(RefreshToken.for_user(self.user))
    
#     def test_logout_success(self):
#         """
#         Test that providing a valid refresh token blacklists the token
#         and returns a 200 response with a success message.
#         """
#         response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn("success", response.data)
#         self.assertEqual(response.data["success"], "Logged out successfully")
    
#     def test_logout_missing_refresh_token(self):
#         """
#         Test that when no refresh token is provided,
#         the view returns a 400 error with the expected message.
#         """
#         response = self.client.post(self.url, {}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Tokens are required")
    
#     def test_logout_invalid_refresh_token(self):
#         """
#         Test that providing an invalid refresh token results in a 500 error.
#         (This test assumes that RefreshToken() will throw an exception
#         when given an invalid token.)
#         """
#         invalid_token = "invalidtoken"
#         response = self.client.post(self.url, {"refresh": invalid_token}, format="json")
#         self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#         self.assertIn("error", response.data)
#         # The error message might vary; check that it indicates an issue with token validity.
#         self.assertIn("Token is invalid or expired", response.data["error"])
    
#     def test_logout_blacklist_failure(self):
#         """
#         Test that if token.blacklist() fails (simulated via patch),
#         the view catches the exception and returns a 500 error.
#         """
#         with patch.object(RefreshToken, 'blacklist', side_effect=Exception("Blacklist failed")):
#             response = self.client.post(self.url, {"refresh": self.refresh_token}, format="json")
#             self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
#             self.assertIn("error", response.data)
#             self.assertEqual(response.data["error"], "Blacklist failed")