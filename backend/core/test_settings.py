from .settings import *

# Use SQLite for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Disable migrations for speed
# MIGRATION_MODULES = {app: None for app in INSTALLED_APPS}

# Use a faster password hasher
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Ensure we have a secret key
SECRET_KEY = 'test-secret-key'
