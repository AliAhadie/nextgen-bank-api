import random
import string

def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    digits = string.digits
    otp = ''.join(random.choice(digits) for _ in range(length))
    return otp


def generate_username()-> str:
    """Generate a unique username for a bank user."""
    prefix = 'BankUser-'
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    username = prefix + suffix
    return username