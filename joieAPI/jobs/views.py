from rest_framework import viewsets

from jobs.serializers import JobListTypeSerializer
from jobs.models import JobListType, Job


class JobListTypeViewSet(viewsets.ModelViewSet):
    """
    this view set is used by admin user for JobListType models management
    """
    serializer_class = JobListTypeSerializer
    queryset = JobListType.objects.all()