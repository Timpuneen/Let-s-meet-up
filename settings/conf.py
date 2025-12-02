import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()

try:
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
except FileNotFoundError:
    pass 

ENV_POSSIBLE_OPTIONS = ['local', 'prod']

ENV_ID = env('MEETUP_ENV_ID', default='local')

assert ENV_ID in ENV_POSSIBLE_OPTIONS, (
    f"Invalid MEETUP_ENV_ID: '{ENV_ID}'. "
    f"Must be one of {ENV_POSSIBLE_OPTIONS}"
)

SECRET_KEY = env('SECRET_KEY', default='django-insecure-$y!e)2qbr-stk^w^b!5&nthyao6q!h_n6)y^2cpj-t=vzw1t&t')

__all__ = ['ENV_ID', 'ENV_POSSIBLE_OPTIONS', 'SECRET_KEY', 'env', 'BASE_DIR']
