"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env file
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# Fetch the Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# SECURITY WARNING: keep the secret key used in production secret!

# SECRET_KEYS
SECRET_KEY = os.getenv("SECRET_KEY")
PRIVATE_KEY = open(os.path.join(BASE_DIR, "private_key.pem")).read()
PUBLIC_KEY = open(os.path.join(BASE_DIR, "public_key.pem")).read()

# URLS
HTTPS = os.getenv("HTTPS")
BASE_ROUTE = os.getenv("FRONTEND_BASE_ROUTE")

if HTTPS == "True":
    BACKEND_URL = os.getenv("HTTPS_BACKEND_URL")
    FRONTEND_URL = os.getenv("HTTPS_FRONTEND_URL")
else:
    BACKEND_URL = os.getenv("BACKEND_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", 'False') == 'True'

TESTING = os.getenv("TESTING", 'False') == 'True'

# Allowed Hosts
if ENVIRONMENT == "Development":
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'localhost:8000']
else:
    ALLOWED_HOSTS = []


# Application definition

APP_NAME = os.getenv("APP_NAME")

INSTALLED_APPS = [
    'core_db',
    'auth_api',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'social_django',
    'drf_spectacular',
    'phonenumber_field',
    'phone_verify',
    
    'django_filters',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE'),
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST', 'localhost'),
        'PORT': os.getenv('DATABASE_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication backends

AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    # 'social_core.backends.instagram.InstagramOAuth2',
    # 'social_core.backends.twitter.TwitterOAuth',
    # 'social_core.backends.linkedin.LinkedinOAuth2',
    'social_core.backends.github.GithubOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Pipelines

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'auth_api.pipeline.user_creation',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'social_core.pipeline.user.user_details',
)

# Social django settings

SOCIAL_AUTH_JSONFIELD_ENABLED = True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv("GOOGLE_CLIENT_ID")
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = ['email', 'profile']

SOCIAL_AUTH_FACEBOOK_KEY = os.getenv("FACEBOOK_CLIENT_ID")
SOCIAL_AUTH_FACEBOOK_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id,name,email,picture.width(500).height(500)',
}

SOCIAL_AUTH_GITHUB_KEY = os.getenv("GITHUB_CLIENT_ID")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# SOCIAL_AUTH_INSTAGRAM_KEY = '<INSTAGRAM_CLIENT_ID>' # business app required
# SOCIAL_AUTH_INSTAGRAM_SECRET = '<INSTAGRAM_CLIENT_SECRET>'

# SOCIAL_AUTH_TWITTER_KEY = '<TWITTER_API_KEY>' # privacy policy link required
# SOCIAL_AUTH_TWITTER_SECRET = '<TWITTER_API_SECRET>'

# SOCIAL_AUTH_LINKEDIN_KEY = '<LINKEDIN_CLIENT_ID>' # LinkedIn page required
# SOCIAL_AUTH_LINKEDIN_SECRET = '<LINKEDIN_CLIENT_SECRET>'

# Twilio Settings

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Recaptcha Settings
RECAPTCHA_SITE_KEY = os.getenv("RECAPTCHA_SITE_KEY")
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")

# REST Framework Settings

# Never give comma after drf_spectacular.openapi.AutoSchema
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': (
        'drf_spectacular.openapi.AutoSchema'
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
        "rest_framework.permissions.IsAdminUser",
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'email_otp': '1/min',
        'email_verify': '1/min',
        'password_reset': '1/min',
        'phone_otp': '1/min',
    },
    'ORDERING_PARAM': 'ordering',
}

# Simple JWT Settings

REST_USE_JWT = True

SIMPLE_JWT = {
    # 10 second window for access_token_expiry setup
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5, seconds=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    
     # Set the RS256 algorithm
    "ALGORITHM": "RS256",
    
    # Set the private key for signing the token
    "SIGNING_KEY": PRIVATE_KEY,
    
    # Set the public key for verifying the token
    "VERIFYING_KEY": PUBLIC_KEY,
    
    # Token Settings
    "USER_ID_CLAIM": "user_id",
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

# CORS Settings

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.56.1:3000",
    "https://localhost",
    "https://127.0.0.1",
    "https://192.168.56.1",
]

CORS_ALLOW_CREDENTIALS = True

# CSRF Settings

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000",
    "http://192.168.56.1:3000",
    "https://localhost",
    "https://127.0.0.1",
    "https://192.168.56.1",
]

CSRF_COOKIE_SECURE = True  # Ensures the CSRF cookie is sent only over HTTPS
CSRF_COOKIE_HTTPONLY = True  # Must be False since JavaScript needs to read the token
CSRF_COOKIE_SAMESITE = 'Lax' # Prevent cross-origin requests
CSRF_COOKIE_AGE = 60 * 60 * 24 # 1 day

AUTH_USER_MODEL = 'core_db.User'

# Media Settings

if TESTING:
    MEDIA_URL = '/media/test_media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media', 'test_media')
else:
    MEDIA_URL = 'https://localhost/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, '..', 'media')
    
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
    
# Email Settings
    
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER')
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')