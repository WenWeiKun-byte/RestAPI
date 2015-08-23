from django.db import models
from authentication.models import Company, JOIE


class CoyJOIEDB(models.Model):
    """
    the db of the company to maintain the JOIE

    """
    company = models.OneToOneField(Company)
    joie = models.OneToOneField(JOIE)
    job_rate = models.FloatField()

    class Meta:
        db_table = 'joie_coy_joie_db'
