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
    multiple_job_rates = models.BooleanField(default=False)

    class Meta:
        db_table = 'joie_coy_joie_db'

    # for ModelChoiceField use
    def get_name(self):
        return self.company.name

    def get_job_rate(self):
        if self.multiple_job_rates:
            return "%s+" % self.job_rate
        else:
            return self.job_rate


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
    joie = models.ForeignKey(JOIE)
    coy_joie_db = models.ForeignKey(CoyJOIEDB)
    clock_in = models.DateTimeField()
    clock_out = models.DateTimeField()
    break_duration = models.PositiveIntegerField()  # cannot use break keyword
    remarks = models.TextField()  # JOIE can write feedback to emp
    feedback = models.OneToOneField(FeedBack, related_name='timesheet')

    STATUS = Choices('approved', 'pending', 'rejected', 'draft', 'archived')
    status = StatusField(default=STATUS.draft)

    class Meta:
        db_table = 'joie_timesheet'

