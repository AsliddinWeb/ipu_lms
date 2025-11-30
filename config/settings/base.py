from pathlib import Path

import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Local APPS
    'apps.accounts',
    'apps.courses',
    'apps.assessments',
    'apps.attendance',
    'apps.analytics',
    'apps.content',
    'apps.main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / '../templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, '../static')]
STATIC_ROOT = os.path.join(BASE_DIR, '../staticfiles')

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, '../media/')

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram bot
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


# Accounts
AUTH_USER_MODEL = 'accounts.User'

# Login urls
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# AI Chatbot
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Universitet ma'lumotlari (AI context uchun)
UNIVERSITY_INFO = """
IPU - Inha University in Tashkent haqida ma'lumot:

📍 Manzil: Toshkent shahri, Mirzo Ulug'bek tumani, Ziyolilar ko'chasi, 9-uy
📞 Telefon: +998 71 289 99 99
📧 Email: info@inha.uz
🌐 Website: https://inha.uz

👨‍💼 Rektor: Prof. Dr. Muzaffar Djalalov
👨‍💼 Prorektor: Prof. Dr. Kim Young-Chul

📚 Fakultetlar:
1. Axborot texnologiyalari fakulteti (IT)
2. Iqtisodiyot va menejment fakulteti
3. Logistika va biznes fakulteti

⏰ Ish vaqti: Dushanba - Juma, 09:00 - 18:00
📅 O'quv yili: Sentyabr - Iyun

💰 Kontrakt narxi: 22,000,000 - 33,000,000 so'm (yo'nalishga qarab)

🎓 Talabalar soni: 3000+ 
👨‍🏫 O'qituvchilar: 200+

📋 Qabul hujjatlari:
- Pasport nusxasi
- Diplom yoki attestat
- 3x4 rasm (6 dona)
- Tibbiy ma'lumotnoma (086)

🏆 Yutuqlar:
- Janubiy Koreya Inha University hamkorligi
- Xalqaro diplom
- Koreys tili o'qitiladi
"""
