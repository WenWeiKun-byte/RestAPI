from django.db import models
from django.core import validators
from authentication.models import Employer, JOIEUtil, JOIE
from model_utils.fields import StatusField
from model_utils import Choices
from django.conf import settings


class JobListType(models.Model):
    """
    pre-created models;
    Chosen during the job creation process
    """
    TYPE_NORMAL = 1
    TYPE_PREMIUM_ADVERT = 2
    TYPE_LAST_MINUTE_ADVERT = 3
    list_type_choice = ((1, 'Normal'), (2, 'Premium Advert'), (3, 'Last Minute Advert'))
    list_type = models.IntegerField(choices=list_type_choice, unique=True, error_messages={
        'unique': "This type already exists.",
    })
    description = models.TextField(blank=True)

    # for ModelChoiceField use
    def get_name(self):
        return self.list_type

    def __unicode__(self):
        return self.list_type

    class Meta:
        db_table = 'joie_job_list_type'


class SupportImage(models.Model):
    image_1 = models.ImageField(upload_to='support', blank=True, null=True)
    image_2 = models.ImageField(upload_to='support', blank=True, null=True)
    image_3 = models.ImageField(upload_to='support', blank=True, null=True)
    image_4 = models.ImageField(upload_to='support', blank=True, null=True)
    image_5 = models.ImageField(upload_to='support', blank=True, null=True)
    image_6 = models.ImageField(upload_to='support', blank=True, null=True)

    class Meta:
        db_table = 'joie_job_support_image'


class Job(JOIEUtil, models.Model):
    """
    Created by Employers
    A job listing created by employers to allow JOIEs to apply
    """
    # job_id will be assigned after published
    job_id = models.CharField(max_length=30, unique=True, null=True, blank=True)

    owner = models.ForeignKey(Employer, related_name='job_list')
    job_list_type = models.ForeignKey(JobListType)
    applicants = models.ManyToManyField(JOIE, through='Application', blank=True, related_name='job_list')

    title = models.CharField(max_length=50)
    detail = models.TextField()
    job_rate = models.FloatField()
    postal_code = models.TextField(validators=[
        validators.RegexValidator(r'^(\d{6},?)*\d{6}$',
                                  'Example format will be 123456,654321 or just 123456', 'invalid'),
    ])

    keywords = models.TextField(blank=True, validators=[
        validators.RegexValidator(r'^(\w+,?){0,4}\w+$',
                                  'Up to a limit of 5 keywords, separated by a comma.', 'invalid'),
    ])
    short_description = models.TextField(blank=True)
    promotion_banner = models.ImageField(upload_to='banner', max_length=100, blank=True, null=True)
    STATUS = Choices(*settings.JOB_STATUS)
    status = StatusField(default=STATUS.draft)
    time_of_publish = models.DateTimeField(blank=True, null=True)
    # release date will not accurate to Time, easy for cronjob
    time_of_release = models.DateField(blank=True, null=True)
    # Empty field will denotes job be published indefinitely.
    support_image = models.OneToOneField(SupportImage, blank=True, null=True, related_name='job')
    multiple_job_rates = models.BooleanField(default=False)

    class Meta:
        db_table = 'joie_job'

    def __unicode__(self):
        return self.title

    def get_applicant_number(self):
        return self.applicants.count()

    def get_job_rate(self):
        if self.multiple_job_rates:
            return "%s+" % self.job_rate
        else:
            return self.job_rate



class Application(models.Model):
    """
    Created when JOIE applies for job
    """
    job = models.ForeignKey(Job)
    applicant = models.ForeignKey(JOIE)

    time_of_apply = models.DateTimeField(auto_now_add=True)
    STATUS = Choices('approved', 'pending', 'rejected')
    status = StatusField(default=STATUS.pending)

    class Meta:
        db_table = 'joie_application'

