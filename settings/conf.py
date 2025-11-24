"""
Environment configuration module for Let's Meet Up project.

This module handles environment selection and validation using the
MEETUP_ENV_ID environment variable. Follows djangorlal's conf.py pattern.
"""

import os
from pathlib import Path
import environ

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize django-environ
env = environ.Env()

# Read .env file from project root
try:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except FileNotFoundError:
    pass  # .env file is optional

# Define possible environment options
ENV_POSSIBLE_OPTIONS = ['local', 'prod']

# Get environment ID from environment variable
ENV_ID = env('MEETUP_ENV_ID', default='local')

# Validate environment ID
assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Invalid MEETUP_ENV_ID: '{ENV_ID}'. "
    f"Must be one of {ENV_POSSIBLE_OPTIONS}"
)

# Export SECRET_KEY - read from environment variable
SECRET_KEY = env('SECRET_KEY', default='django-insecure-$y!e)2qbr-stk^w^b!5&nthyao6q!h_n6)y^2cpj-t=vzw1t&t')

# Export env object and other variables for use in other settings modules
__all__ = ['ENV_ID', 'ENV_POSSIBLE_OPTIONS', 'SECRET_KEY', 'env', 'BASE_DIR']
