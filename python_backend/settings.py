"""
Django settings for python_backend project.

Generated by 'django-admin startproject' using Django 2.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import os
import datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0bjj=yvus#i%_cr)rh-o#r=7z@p6q1bdg(z(9n)qlzpz!)#nns'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']



# 用户系统
AUTH_USER_MODEL = 'account.AccountInfo'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'misc.pagenumber.pagenumber.MyPageNumberPagination',
    'PAGE_SIZE': 10,

    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'misc.permissions.permissions.FuncPermission',
        'misc.permissions.permissions.DontCheckRoot'
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer'),

    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),

    'NON_FIELD_ERRORS_KEY': 'non_field_errors',
}

JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER':
        'account.utils.jwt_response_payload_handler',

    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=30000),
}

AUTHENTICATION_BACKENDS = {
    'misc.backends.backends.AccountBackend',
}
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'account',
    'expert',
    'achievement',
    'public_models',
    'news',
    'public_tools',
    'rest_framework',
    'rest_framework_jwt',
    'django_filters',
    'rest_framework_swagger',
    'gunicorn', # 中间件
    'corsheaders',# 跨域(以后删除)
    'projectmanagement',#项目管理
    'consult',#征询管理
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',

    'corsheaders.middleware.CorsMiddleware',# 跨域(以后删除)

    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 跨域增加忽略(以后删除)
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*'
)
#跨域(以后删除)
CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)
#跨域(以后删除)
CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'token',
)

ROOT_URLCONF = 'python_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['frontend/dist'],
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

WSGI_APPLICATION = 'python_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

if os.environ.get('DATABASE_DEBUG', None):
    print(1)
    database_setting = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'test_PatClub',
        'HOST': '120.77.58.203',
        'PORT': 3306,
        'USER': 'forcar',
        'PASSWORD': 'l0092687dd'
    }
    redis_setting = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:l0092687dd@120.77.58.203:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
else:
    print(0)
    database_setting = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'PatClub',
        'HOST': '127.0.0.1',
        'PORT': 3306,
        'USER': 'root',
        'PASSWORD': 'l0092687dd'
    }


    redis_setting = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://:l0092687dd@127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }

DATABASES = {
    'default': database_setting
}

# redis 数据库默认1号

CACHES = {
    "default": redis_setting
}
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
#SESSION_CACHE_ALIAS = "session"



# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

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

# 上传附件用的测试数据,部署到线上后在修改
DEFAULT_FILE_STORAGE = 'backends.ImageStorage'
MEDIA_ROOT = '/alidata1/patclub/temp/uploads/temporary/'#部署后将此地址改为正式的临时目录
BASE_URL= 'http://patclub.for8.cn:8764/'#此地址根据图片服务器的真实地址而定
media_root_front = 'http://patclub.for8.cn:8764/temp/uploads/temporary/'#此地址为抛给前端的地址
# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(lineno)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(module)s %(lineno)d %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, "logs/python_backend.log"),  # 日志文件的位置
            'maxBytes': 300 * 1024 * 1024,
            'backupCount': 10,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        'django': {  # 定义了一个名为django的日志器
            'handlers': ['console', 'file'],
            'propagate': True,
        },
    }
}

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False #改为False 解决插入数据库时间小于当前8个小时的问题


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "frontend/dist/static"),
]
STATIC_ROOT = os.path.join(BASE_DIR , "static/")

# 登陆后全开放接口
public_url = ['/docs/', '/public/uploadment', '/public/uploadment/','/project/project_step_info/']
