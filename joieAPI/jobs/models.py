from django.db import models
from authentication.models import Employer, JOIEUtil, JOIE
from model_utils.fields import StatusField
from model_utils import Choices


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

    class Meta:
        db_table = 'joie_job_list_type'


class Job(JOIEUtil, models.Model):
    """
    Created by Employers
    A job listing created by employers to allow JOIEs to apply
    """
    # job_id will be assigned after published
    job_id = models.IntegerField(unique=True, null=True, blank=True)

    owner = models.ForeignKey(Employer, related_name='job_list')
    job_list_type = models.OneToOneField(JobListType)
    applicants = models.ManyToManyField(JOIE, through='Application', blank=True, related_name='job_list')

    title = models.CharField(max_length=50)
    detail = models.TextField()
    promotion_banner = models.ImageField(upload_to='banner', max_length=100, blank=True, null=True)
    STATUS = Choices('active', 'suspended', 'archived', 'suspended', 'draft')
    status = StatusField(default=STATUS.draft)
    job_rate = models.FloatField()

    time_of_published = models.DateTimeField(blank=True, null=True)
    # release date will not accurate to Time, easy for cronjob
    time_of_release = models.DateField()

    class Meta:
        db_table = 'joie_job'

    def __unicode__(self):
        return self.title


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



