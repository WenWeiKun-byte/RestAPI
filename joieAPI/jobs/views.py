from rest_framework import viewsets, filters, mixins
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from datetime import datetime, date
from django.utils import timezone
from rest_framework_extensions.mixins import NestedViewSetMixin

from jobs.serializers import JobListTypeSerializer, JobDraftSerializer, JobActiveSerializer, JobSerializer, \
    ApplicationEmpSerializer, ApplicationJOIESerializer
from jobs.models import JobListType, Job, Employer, JOIE, Application, SupportImage
from joieAPI.adhoc import ActionSerializer, AVAILABLE_ACTIONS, ReadDestroyViewSet
from authentication.permissions import IsAdmin, IsEmployer, IsJOIE, IsActiveUser, IsApplicationOwner
from authentication.serializers import JOIEMESerializer
from timesheet.models import CoyJOIEDB


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
    # queryset = Job.objects.filter(status=Job.STATUS.draft)

    permission_classes = (
        IsEmployer,
        IsActiveUser,   # user should be in completed_profile status

    )

    def get_queryset(self):
        user = self.request.user
        emp = Employer.objects.get(user=user)
        return Job.objects.filter(status=Job.STATUS.draft, owner=emp)

    def perform_create(self, serializer):
        owner_user = self.request.user
        serializer.save(owner_user=owner_user)

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
                draft_job.time_of_publish = timezone.now()
                now = datetime.now().strftime('%Y%m%d%H%M%S%f') + '%s' % pk
                draft_job.job_id = now
                draft_job.save()
                return Response({'status': 'job published'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ActiveJobViewSet(NestedViewSetMixin, ReadDestroyViewSet):
    """
    Manage the published jobs
    Modify by Employers
    Including copy as draft for an existing job, remove job to archive folder, view job applicants, approval
    """

    serializer_class = JobActiveSerializer
    # queryset = Job.objects.filter(status=Job.STATUS.active, time_of_release__gt=date.today)

    permission_classes = (
        IsEmployer,
        IsActiveUser,

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
                new_draft.detail = current_job.detail
                new_draft.time_of_release = current_job.time_of_release
                new_draft.short_description = current_job.short_description
                if current_job.support_image.all():
                    for image in current_job.support_image:
                        SupportImage.objects.create(job=new_draft, image=image.image)
                new_draft.postal_code = current_job.postal_code
                new_draft.keywords = current_job.keywords
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


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.filter(status=Job.STATUS.active, time_of_release__gt=date.today)

    @detail_route(methods=['post'], permission_classes=[IsJOIE])
    def apply(self, request, pk=None):
        """
        JOIE apply for an active JOB
        :param request:
        :param pk:
        :return: create a new application if success.
        """
        serializer = ActionSerializer(data=request.data)
        current_job = self.get_object()
        account = self.request.user
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['JOB_APPLY']:
                joie = JOIE.objects.get(user=account)
                application, created = Application.objects.get_or_create(applicant=joie, job=current_job)
                if not created:
                    return Response({'status': 'you have applied for this job before'})
                return Response({'status': 'job apply successfully'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ApplicationEmpViewSet(NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for employers to manage the applications based on jobs
    """
    serializer_class = ApplicationEmpSerializer
    queryset = Application.objects.all()

    permission_classes = (
        IsApplicationOwner,
    )

    filter_backends = (filters.DjangoFilterBackend, )
    filter_fields = ('status',)

    @detail_route(methods=['post'])
    def approve(self, request, pk=None, parent_lookup_job_id=None):
        """
        owner can approve the current application
        :param request:
        :param pk:
        :return: change the application's status to 'approved' if success
        """
        serializer = ActionSerializer(data=request.data)
        current_app = self.get_object()
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['JOB_APPROVE']:
                if current_app.status == Application.STATUS.pending:
                    current_app.status = Application.STATUS.approved
                    current_app.save()
                    # then add JOIE to the DB or the company
                    company = current_app.job.owner.company
                    joie = current_app.applicant
                    job_rate = current_app.job.job_rate
                    CoyJOIEDB.objects.get_or_create(company=company, joie=joie, job_rate=job_rate)
                    return Response({'status': 'application approve successfully'})
                else:
                    return Response({'status': 'it is not a pending application'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def reject(self, request, pk=None, parent_lookup_job_id=None):
        """
        owner can reject the current application
        :param request:
        :param pk:
        :return: change the application's status to 'rejected' if success
        """
        serializer = ActionSerializer(data=request.data)
        current_app = self.get_object()
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['JOB_REJECT']:
                if current_app.status == Application.STATUS.pending:
                    current_app.status = Application.STATUS.rejected
                    current_app.save()
                    return Response({'status': 'application rejected'})
                else:
                    return Response({'status': 'it is not a pending application'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class ApplicantsViewSet(NestedViewSetMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    payed employers can view the details info of the applicants
    """
    serializer_class = JOIEMESerializer
    permission_classes = (
        IsEmployer,
    )
    queryset = JOIE.objects.all()


class ApplicationJOIEViewSet(ReadDestroyViewSet):
    serializer_class = ApplicationJOIESerializer
    permission_classes = (
        IsJOIE,
    )

    def get_queryset(self):
        user = self.request.user
        joie = JOIE.objects.get(user=user)
        return Application.objects.filter(applicant=joie)

    def perform_destroy(self, instance):
        """
        only status 'pending' may be deleted
        :param instance:
        :return:
        """
        if instance.status == Application.STATUS.pending:
            instance.delete()

        else:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)