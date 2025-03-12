MIDDLEWARE = [
    'blog.middleware.TwoFactorMiddleware',
]

TIME_ZONE = 'America/Bogota'
USE_TZ = True

TEMPLATES = [
    {
        'OPTIONS': {
            'context_processors': [
                'client_portal.context_processors.user_role',
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
] 