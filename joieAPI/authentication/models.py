from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from model_utils.fields import StatusField
from model_utils import Choices


class AccountManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """
        this method will expose to API
        """
        if not email:
            raise ValueError('Users must have a valid email address.')
        # username is not a necessary field
        # if not kwargs.get('username'):
        # raise ValueError('Users must have a valid username.')

        user = self.model(
            email=self.normalize_email(email), **kwargs)

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **kwargs):
        """
        this method used for creating superadmin
        :param email:
        :param password:
        :param kwargs:
        :return:
        """
        account = self.create_user(email, password, **kwargs)

        account.is_admin = True
        account.is_superAdmin = True
        account.is_active = True
        account.app_user_type = None
        account.save()

        return account

    def create_admin(self, email, password, **kwargs):
        """
        this method will be only used by superadmin
        :param email:
        :param password:
        :param kwargs:
        :return:
        """
        account = self.create_user(email, password, **kwargs)

        account.is_admin = True
        account.is_active = True
        account.app_user_type = None
        account.save()

        return account


class JOIEUtil(models.Model):
    """
    attributes for monitoring the models
    """
    create_at = models.DateTimeField(auto_now_add=True)
    create_by = models.CharField(max_length=40, blank=True)
    update_at = models.DateTimeField(auto_now=True)
    update_by = models.CharField(max_length=40, blank=True)

    class Meta:
        abstract = True


class User(AbstractBaseUser, JOIEUtil):
    """
    basic model for auth
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)

    is_admin = models.BooleanField(default=False)
    is_superAdmin = models.BooleanField(default=False)

    app_user_type_choices = (('Employer', 'Employer'), ('JOIE', 'JOIE'))
    app_user_type = models.CharField(choices=app_user_type_choices, blank=True, null=True, max_length=10)

    is_active = models.BooleanField(default=False,
                                    help_text=('Designates whether this user should be treated as active.'
                                               'Unselect this instead of deleting accounts.'))
    STATUS = Choices('inactive', 'completed_profile', 'special_type_A', 'suspended', 'deleted', 'black_listed')
    status = StatusField(default=STATUS.inactive)
    first_time_sign_in = models.BooleanField(default=True,
                                             help_text=('when user new created, before the first login.'
                                                        'during user first login, user need to update the necessary fields.'))

    objects = AccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []     # used by djoser

    class Meta:
        ordering = ('email',)
        db_table = 'joie_user'

    def __unicode__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_user_type(self):
        return self.app_user_type

    def is_first_time_sign_in(self):
        return self.first_time_sign_in


class SocialLink(models.Model):
    networkName_choices = (
        ('Facebook', 'Facebook'), ('Instagram', 'Instagram'), ('Twitter', 'Twitter'), ('LinkedIn', 'LinkedIn'))
    network_name = models.CharField(choices=networkName_choices, max_length=10)
    link = models.URLField()

    user = models.ForeignKey(User, blank=True, null=True, related_name='socialLinks')

    class Meta:
        db_table = 'joie_social_link'

    def __unicode__(self):
        return self.network_name


class Admin(models.Model):
    user = models.OneToOneField(User, primary_key=True)

    class Meta:
        db_table = 'joie_admin'


class SuperAdmin(models.Model):
    user = models.OneToOneField(User, primary_key=True)

    class Meta:
        db_table = 'joie_super_admin'


class Industry(models.Model):
    """
    new employer create with a empty company with default industry
    industry should not create by normal user
    """
    name = models.CharField(max_length=40, unique=True, default='default')
    description = models.TextField(blank=True)

    def get_name(self):
        return self.name

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'joie_industry'


class Branch(models.Model):
    pass


class Company(models.Model):
    """
    oneToOne relationship with employer model
    """
    company_name = models.CharField(max_length=100, blank=True)
    roc_number = models.CharField(max_length=40, blank=True)
    business_type_choices = (('Direct', 'Direct'), ('Agency', 'Agency'))
    business_type = models.CharField(choices=business_type_choices, blank=True, max_length=10)
    ea_number = models.CharField(max_length=40, blank=True)
    company_address = models.CharField(max_length=100, blank=True)
    company_postal_code = models.IntegerField(blank=True, null=True)
    company_description = models.CharField(max_length=100, blank=True)
    company_contact_person = models.CharField(max_length=40, blank=True)
    company_contact_detail = models.CharField(max_length=100, blank=True)
    company_logo = models.ImageField(upload_to='logo', max_length=100, blank=True, null=True)
    credit_amount = models.FloatField(default=0.00)
    industry = models.ForeignKey(Industry)

    class Meta:
        db_table = 'joie_company'

    def __unicode__(self):
        return self.company_name


class Employer(models.Model):
    user = models.OneToOneField(User, related_name='employer_profile')
    company = models.OneToOneField(Company, related_name='employer')

    def __unicode__(self):
        return '%s From %s ' % (self.user.email, self.company.company_name)

    class Meta:
        db_table = 'joie_employer'

    @receiver(post_save, sender=User)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            user = instance
            if not user.is_admin:
                if user.app_user_type == 'Employer':
                    industry, created = Industry.objects.get_or_create(name='default')
                    company = Company.objects.create(industry=industry)
                    Employer.objects.get_or_create(user=instance, company=company)

    @receiver(pre_delete, sender=User)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            if Employer.objects.get(user=instance):
                user_profile = Employer.objects.get(user=instance)
                company = Company.objects.get(employer=user_profile)
                company.delete()
                user_profile.delete()


class Financial(models.Model):
    bank_number = models.IntegerField(null=True, blank=True)
    branch_number = models.IntegerField(null=True, blank=True)
    account_number = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'joie_financial'


class JOIE(models.Model):
    user = models.OneToOneField(User, related_name='joie_profile')
    financial_detail = models.OneToOneField(Financial, blank=True, related_name='joie')

    nric_num = models.CharField(max_length=20, blank=True)
    name_on_nric = models.CharField(max_length=40, blank=True)
    nric_type_choices = (('Singaporean', 'Singaporean'), ('PR', 'PR'))
    nric_type = models.CharField(choices=nric_type_choices, blank=True, max_length=20)
    date_of_birth = models.DateField(blank=True, null=True)
    preferred_name = models.CharField(max_length=40, blank=True)
    gender_choices = ((0, 'Male'), (1, 'Female'))
    gender = models.CharField(choices=gender_choices, blank=True, max_length=10)
    contact_number = models.CharField(max_length=20, blank=True)

    block_building = models.CharField(max_length=20, blank=True)
    street_name = models.CharField(max_length=20, blank=True)
    unit_number = models.CharField(max_length=20, blank=True)
    postal_code = models.IntegerField(blank=True, null=True)
    photo = models.ImageField(upload_to='photos', max_length=100, blank=True, null=True)

    punctuality = models.FloatField(default=0.0)
    job_performance = models.FloatField(default=0.0)
    attitude = models.FloatField(default=0.0)
    rating = models.FloatField(default=0.0)

    referred_from = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = 'joie_joie'

    def __unicode__(self):
        return self.user.email

    @receiver(post_save, sender=User)
    def create_profile_for_user(sender, instance=None, created=False, **kwargs):
        if created:
            user = instance
            if not user.is_admin:
                if user.app_user_type == 'JOIE':
                    financial = Financial.objects.create()
                    JOIE.objects.get_or_create(user=instance, financial_detail=financial)

    @receiver(pre_delete, sender=User)
    def delete_profile_for_user(sender, instance=None, **kwargs):
        if instance:
            if JOIE.objects.get(user=instance):
                joie = JOIE.objects.get(user=instance)
                financial = Financial.objects.get(joie=joie)
                financial.delete()
                joie.delete()