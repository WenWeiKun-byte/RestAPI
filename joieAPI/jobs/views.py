from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from datetime import datetime, date
from django.utils import timezone

from jobs.serializers import JobListTypeSerializer, JobDraftSerializer, JobActiveSerializer
from jobs.models import JobListType, Job, Employer, JOIE
from joieAPI.adhoc import ActionSerializer, AVAILABLE_ACTIONS, ReadDestroyViewSet
from authentication.permissions import IsAdmin, IsEmployer, IsJOIE, IsActiveUser


class JobListTypeViewSet(viewsets.ModelViewSet):
    """
    this view set is used by admin user for JobListType models management
    """
    permission_classes = (
        IsAdmin,
    )
    serializer_class = JobListTypeSerializer
    queryset = JobListType.objects.all()


class DraftJobViewSet(viewsets.ModelViewSet):
    """
    this view set for the job draft box use
    including create, list, update, retrieve, delete
    """
    serializer_class = JobDraftSerializer
    queryset = Job.objects.filter(status=Job.STATUS.draft)

    permission_classes = (
        IsActiveUser,
        IsEmployer
    )

    def get_queryset(self):
        user = self.request.user
        emp = Employer.objects.get(user=user)
        return Job.objects.filter(status=Job.STATUS.active, time_of_release__gt=date.today, owner=emp)

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


class ActiveJobViewSet(ReadDestroyViewSet):
    """
    Manage the published jobs
    Modify by Employers
    Including copy as draft for an existing job, remove job to archive folder, view job applicants, approval
    """

    serializer_class = JobActiveSerializer
    # queryset = Job.objects.filter(status=Job.STATUS.active, time_of_release__gt=date.today)

    permission_classes = (
        IsActiveUser,
        IsEmployer
    )

    def get_queryset(self):
        user = self.request.user
        emp = Employer.objects.get(user=user)
        return Job.objects.filter(status=Job.STATUS.active, time_of_release__gt=date.today, owner=emp)

    @detail_route(methods=['post'])
    def copy(self, request, pk=None):
        """
        copy the current job as a draft

        """
        serializer = ActionSerializer(data=request.data)
        current_job = self.get_object()
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['JOB_COPY']:
                new_draft = Job()
                new_draft.owner = current_job.owner
                new_draft.job_list_type = current_job.job_list_type
                new_draft.status = Job.STATUS.draft
                new_draft.job_rate = current_job.job_rate
                new_draft.promotion_banner = current_job.promotion_banner
                new_draft.title = current_job.title
                new_draft.time_of_release = current_job.time_of_release
                new_draft.save()
                return Response({'status': 'new draft job saved'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def perform_destroy(self, instance):
        """
        will not delete the job object, but update the status to archived
        :param instance: current job
        :return:
        """
        instance.stats = Job.STATUS.archived
        instance.save()
