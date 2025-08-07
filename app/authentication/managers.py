from django.contrib.auth.models import BaseUserManager
from .utils import generate_username




class UserManager(BaseUserManager):
    """Custom manager for the User model."""

    def create_user(self, email:str, password:str=None,**extra_fields):
        """Create and return a user with an email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        username = generate_username()

        user = self.model(email=email, username=username,   **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user


    def create_superuser(self, email:str, password:str=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        user=self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        
        user.save(using=self._db)
        return user

