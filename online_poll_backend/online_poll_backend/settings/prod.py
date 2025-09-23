from .base import *

DEBUG = False
#ALLOWED_HOSTS = ["example.com", "www.example.com"]
ALLOWED_HOSTS = ["*"]

# ✅ Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
