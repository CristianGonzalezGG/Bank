MIDDLEWARE = [
    'blog.middleware.TwoFactorMiddleware',
]

TIME_ZONE = 'America/Bogota'
USE_TZ = True

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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'blog.apps.BlogConfig',
    'client_portal.apps.ClientPortalConfig',
    'formularios.apps.FormulariosConfig',
    'blog',
]

LOGIN_URL = 'blog:login'
LOGIN_REDIRECT_URL = 'blog:home'
LOGOUT_REDIRECT_URL = 'blog:home'

LOGIN_EXEMPT_URLS = [
    r'^inversiones/$',
    r'^proyecciones/$',
    # ... otras URLs públicas ...
] 