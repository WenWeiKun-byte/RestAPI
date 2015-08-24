from django.db import models
from authentication.models import Company, JOIE, Employer
from jobs.models import Job
from model_utils.fields import StatusField
from model_utils import Choices


class CoyJOIEDB(models.Model):
    """
    the db of the company to maintain the JOIE

    """
    company = models.OneToOneField(Company)
    joie = models.OneToOneField(JOIE)
    job_rate = models.FloatField()

    class Meta:
        db_table = 'joie_coy_joie_db'


class FeedBack(models.Model):
    """
    FeedBack info created by emp
    """
    # employer = models.OneToOneField(Employer)
    # joie = models.OneToOneField(JOIE)
    # job = models.OneToOneField(Job)
    feedback = models.TextField()
    punctuality = models.FloatField(default=0.0)
    performance = models.FloatField(default=0.0)
    attitude = models.FloatField(default=0.0)

    class Meta:
        db_table = 'joie_feedback'


class TimeSheet(models.Model):
    """
    TimeSheet created by JOIE
    submit to employer for approval follow up with the payment
    """
    joie = models.OneToOneField(JOIE)
    coy_joie_db = models.OneToOneField(CoyJOIEDB)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField()
    break_duration = models.PositiveIntegerField()  # cannot use break keyword
    remarks = models.TextField()  # JOIE can write feedback to emp
    feedback = models.OneToOneField(FeedBack)

    STATUS = Choices('approved', 'pending', 'rejected')
    status = StatusField(default=STATUS.pending)

    class Meta:
        db_table = 'joie_timesheet'

