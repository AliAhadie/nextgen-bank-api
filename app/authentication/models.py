from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
import uuid
from .utils import generate_otp
from datetime import timedelta
from django.utils import timezone
from .managers import UserManager

# Constants for login attempt duration
LOCK_OUT_DURATION = timedelta(minutes=10)
LOGIN_ATTEMPT_LIMIT=3


class SecurityQuestion(models.TextChoices):
    MAIDEN_NAME = 'maiden_name', _("What is your mother's maiden name?")
    FAVORITE_COLOR = 'favorite_color', _("What is your favorite color?")
    BIRTH_CITY = 'birth_city', _("What is the city where you were born?")
    CHILDHOOD_FRIEND = 'childhood_friend', _("What is the name of your childhood best friend?")
           
    

class AccountStatus(models.TextChoices):
    ACTIVE = "active", _("Active")
    LOCKED = "locked", _("Locked")

class UserRole(models.TextChoices):

    CUSTOMER = "customer", _("Customer")
    ACCOUNT_EXECUTIVE = "account_executive", _("Account Executive")
    TELLER = "teller", _("Teller")
    BRANCH_MANAGER = "branch_manager", _("Branch Manager")


""" coustom user model for the application """
class User(AbstractBaseUser):
    id=models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name=_("ID")
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name=_("Username")
    )
    email = models.EmailField(
        max_length=255,
        unique=True,
        verbose_name=_("Email"),
       db_index=True
    )
    security_question = models.CharField(
        max_length=50,
        choices=SecurityQuestion.choices,
        verbose_name=_("Security Question")
    )
    security_answer = models.CharField(
        max_length=255,
        verbose_name=_("Security Answer")
    )
    first_name = models.CharField(
        max_length=30,
        verbose_name=_("First Name")
    )
    last_name = models.CharField(   
        max_length=30,
        verbose_name=_("Last Name")
    )
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        verbose_name=_("Role")
    )
    account_status = models.CharField(
        max_length=20,
        choices=AccountStatus.choices,
        default=AccountStatus.ACTIVE,
        verbose_name=_("Account Status")
    )
    id_no = models.PositiveIntegerField(
        unique= True,
        verbose_name=_("ID Number")
    )
    failed_login_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("Failed Login Attempts")
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Last Failed Login")
    )
    otp= models.CharField(
        max_length=6,
        null=True,
        blank=True,
        verbose_name=_("One-Time Password (OTP)")
    )
    otp_expiry = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("OTP Expiry")
    )

    objects = UserManager()  # Assuming UserManager is defined elsewhere
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [ 'first_name', 'last_name', 'id_no', 'security_question', 'security_answer', 'role']


    def set_otp(self) -> None:
        """ Generate and send a one-time password (OTP) to the user.
        """
        self.otp = generate_otp()
        self.otp_expiry = timezone.now() + timedelta(minutes=5)
        self.save()
        # Code to send OTP via email or SMS goes here

    def verify_otp(self,otp:str)-> bool:
        """ verify otp token """
        if self.otp==otp and self.otp_expiry > timezone.now():
            self.otp='' 
            self.otp_expiry=None
            self.save()
            return True
        return False

    def handel_failed_login_attempts(self) -> None:
        """handel login failed"""
        self.failed_login_attempts+=1
        self.last_failed_login = timezone.now()
        if self.failed_login_attempts >= LOGIN_ATTEMPT_LIMIT:
            self.account_status=AccountStatus.LOCKED
            self.save()
            #send_account_email_locked(self)
        self.save()

    def unlock_account(self)-> None:
        """Unlock the user's account if it is locked."""

        if self.account_status==AccountStatus.LOCKED:
            self.account_status=AccountStatus.ACTIVE
            self.failed_login_attempts=0
            self.last_failed_login= None
            self.save()


    @property
    def is_locked_out(self) -> bool:
        """Check if the user's account is locked out due to failed login attempts."""
        if self.account_status==AccountStatus.LOCKED:
            if self.last_failed_login and (timezone.now() - self.last_failed_login) >= LOCK_OUT_DURATION:
                self.unlock_account()
                return False
            return True
        return False
    
    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"
    

    def __str__(self) -> str:
        """Return a string representation of the user."""
        return f"{self.full_name} ({self.role})"

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ['-id']





