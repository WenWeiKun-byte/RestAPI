from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response

from jobs.serializers import JobListTypeSerializer, JobDraftSerializer
from jobs.models import JobListType, Job


class JobListTypeViewSet(viewsets.ModelViewSet):
    """
    this view set is used by admin user for JobListType models management
    """
    serializer_class = JobListTypeSerializer
    queryset = JobListType.objects.all()


class DraftJobViewSet(viewsets.ModelViewSet):
    """
    this view set for the job draft box use
    including create, list, update, retrieve, delete
    """
    serializer_class = JobDraftSerializer
    queryset = Job.objects.filter(status=Job.STATUS.draft)

    # def create(self, request, *args, **kwargs):
    #     owner = request.user.id
    #     print owner
    #     print request.data
    #     # update owner info at the backend
    #     data = request.data
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        owner = self.request.user.id
        serializer.save(owner=owner)