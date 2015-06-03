from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        this method will expose to API
        """
        print '-------------------------username:' + kwargs.get('username')
        print '-------------------------email:' + email
        if not email:
            raise ValueError('Users must have a valid email address.')

        if not kwargs.get('username'):
            raise ValueError('Users must have a valid username.')

        account = self.model(
            email=self.normalize_email(email), **kwargs)

        account.set_password(password)
        account.save()

        return account

    def create_superuser(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_admin = True
        account.is_staff = True
        account.is_active = True
        account.app_user_type = None
        account.save()

        return account

    def create_staff(self, email, password, **kwargs):
        account = self.create_user(email, password, **kwargs)

        account.is_staff = True
        account.is_active = True
        account.app_user_type = None
        account.save()

        return account


class Account(AbstractBaseUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=40, unique=True)

    is_admin = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    app_user_type_choices = (('Employer', 'Employer'), ('Employee', 'Employee'))
    app_user_type = models.CharField(choices=app_user_type_choices, blank=True, null=True, max_length=10)
    is_active = models.BooleanField(default=True,
                                     help_text=('Designates whether this user should be treated as active.'
                                                'Unselect this instead of deleting accounts.'))
    is_staff = models.BooleanField(default=False)
    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'app_user_type']

    class Meta:
        ordering = ('created_at',)

    def __unicode__(self):
        return self.email

    def get_full_name(self):

        return self.username

    def get_short_name(self):
        return self.username


class EmployerProfile(models.Model):
    user = models.OneToOneField(Account, related_name='employer_profile')

    company_name = models.CharField(max_length=100, blank=True)
    roc_number = models.CharField(max_length=40, blank=True)
    business_type_choices = (('Direct', 'Direct'), ('Agency', 'Agency'))
    business_type = models.CharField(choices=business_type_choices, blank=True, max_length=10)
    company_address = models.CharField(max_length=100, blank=True)
    company_postal_code = models.IntegerField(blank=True, null=True)
    company_description = models.CharField(max_length=100, blank=True)
    company_contact_person = models.CharField(max_length=40, blank=True)
    company_contact_detail = models.CharField(max_length=100, blank=True)
    company_logo = models.ImageField(upload_to='static/logo/', max_length=100, blank=True)
    # optional payment details
    credit_amount = models.IntegerField(blank=True, null=True)
    card_type = models.CharField(max_length=20, blank=True)
    card_number = models.CharField(max_length=20, blank=True)
    name_on_card = models.CharField(max_length=20, blank=True)
    expiration_date = models.CharField(max_length=20, blank=True)
    card_security_code = models.CharField(max_length=10, blank=True)
    billing_address = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=20, blank=True)
    state_province = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    billing_email = models.EmailField(blank=True)

    facebook = models.CharField(max_length=40, blank=True)
    twitter = models.CharField(max_length=40, blank=True)
    instagram = models.CharField(max_length=40, blank=True)

    status_choices = (('0', 'Black Listed'), ('1', 'Inactive'), ('2', 'completed Profile'), ('3', 'Special Type A'))
    status = models.CharField(choices=status_choices,  max_length=20)

    first_time_sign_in = models.BooleanField(default=False)
    last_edited_by = models.CharField(max_length=40)



    def __unicode__(self):
        return self.user.username

    @receiver(post_save, sender=Account)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            user = instance
            if not user.is_staff:
                if user.app_user_type == 'Employer':
                    EmployerProfile.objects.get_or_create(user=instance)

    @receiver(pre_delete, sender=Account)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            if EmployerProfile.objects.get(user=instance):
                user_profile = EmployerProfile.objects.get(user=instance)
                user_profile.delete()


class EmployeeProfile(models.Model):
    user = models.OneToOneField(Account, related_name='employee_profile')

    nric_num = models.CharField(max_length=20, blank=True)
    name_on_nric = models.CharField(max_length=40, blank=True)
    nric_type_choices = (('Singaporean', 'Singaporean'), ('PR', 'PR'))
    nric_type = models.CharField(choices=nric_type_choices, blank=True, max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    preferred_name = models.CharField(max_length=40, blank=True)
    photo = models.ImageField(upload_to='static/photo/', max_length=100, blank=True)
    gender = models.CharField(max_length=20, blank=True)

    contact_number = models.CharField(max_length=20, blank=True)
    block_building = models.CharField(max_length=20, blank=True)
    street_name = models.CharField(max_length=20, blank=True)
    unit_number = models.CharField(max_length=20, blank=True)
    postal_code = models.IntegerField(blank=True, null=True)

    bank_number = models.CharField(max_length=20, blank=True)
    branch_number = models.CharField(max_length=20, blank=True)
    account_number = models.CharField(max_length=10, blank=True)

    feedback_score_punctuality = models.CharField(max_length=20, blank=True)
    feedback_score_job_performance = models.CharField(max_length=20, blank=True)
    feedback_score_attitude = models.CharField(max_length=20, blank=True)
    rating = models.CharField(max_length=20, blank=True)
    referred_from = models.CharField(max_length=40, blank=True)

    facebook = models.CharField(max_length=40, blank=True)
    twitter = models.CharField(max_length=40, blank=True)
    instagram = models.CharField(max_length=40, blank=True)

    status_choices = (('0', 'Black Listed'), ('1', 'Inactive'), ('2', 'completed Profile'))
    status = models.CharField(choices=status_choices,  max_length=20)

    first_time_sign_in = models.BooleanField(default=False)
    last_edited_by = models.CharField(max_length=40)


    def __unicode__(self):
        return self.user.username

    @receiver(post_save, sender=Account)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            user = instance
            if not user.is_staff:
                if user.app_user_type == 'Employee':
                    EmployerProfile.objects.get_or_create(user=instance)

    @receiver(pre_delete, sender=Account)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            if EmployerProfile.objects.get(user=instance):
                user_profile = EmployerProfile.objects.get(user=instance)
                user_profile.delete()