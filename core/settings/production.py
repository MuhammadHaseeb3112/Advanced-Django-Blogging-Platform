from .base import *

DEBUG = False

ALLOWED_HOSTS = ['yourdomain.com']


SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# For production

# CORS_ALLOWED_ORIGINS = [
#     "http://127.0.0.1:3000",
#     "http://localhost:3000",
# ]


# For production

# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True