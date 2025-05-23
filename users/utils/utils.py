import secrets
import string

def generate_random_password(length=16):
    """Generate a secure random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))