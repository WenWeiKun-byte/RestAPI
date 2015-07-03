from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from datetime import datetime
from django.utils import timezone

from jobs.serializers import JobListTypeSerializer, JobDraftSerializer
from jobs.models import JobListType, Job
from joieAPI.adhoc import ActionSerializer, AVAILABLE_ACTIONS


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

    @detail_route(methods=['post'])
    def publish(self, request, pk=None):
        """
        use for draft job publish

        """
        draft_job = self.get_object()
        serializer = ActionSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['JOB_PUBLISH']:
                draft_job.status = Job.STATUS.active
                draft_job.time_of_published = timezone.now()
                now = datetime.now().strftime('%Y%m%d%H%M%S%f') + '%s' % pk
                draft_job.job_id = now
                draft_job.save()
                return Response({'status': 'job published'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)