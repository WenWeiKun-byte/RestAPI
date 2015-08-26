from timesheet.serializers import CoyJOIEDBSerializer, TimeSheet_Joie_Serializer, TimeSheet_Emp_Serializer, FeedbackSerializer
from timesheet.models import CoyJOIEDB, TimeSheet, FeedBack
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from authentication.permissions import IsEmployer, IsJOIE
from authentication.models import Employer, JOIE
from joieAPI.adhoc import ActionSerializer, AVAILABLE_ACTIONS, RetrieveUpdateViewSet
from rest_framework.decorators import detail_route
from rest_framework_extensions.mixins import NestedViewSetMixin


class CoyJOIEDBViewSet(viewsets.ModelViewSet):
    """
    payed employers can view the details info of the applicants
    """
    serializer_class = CoyJOIEDBSerializer
    permission_classes = (
        IsEmployer,
    )

    def get_queryset(self):
        user = self.request.user
        emp = Employer.objects.get(user=user)
        return CoyJOIEDB.objects.filter(company=emp.company)

    def perform_create(self, serializer):
        creator = self.request.user
        emp = Employer.objects.get(user=creator)
        serializer.save(company=emp.company)


class Joie_Timesheet_ViewSet(NestedViewSetMixin, viewsets.ModelViewSet):

    # serializer_class = TimeSheet_Joie_Serializer

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer_class(self):
        """
        return serializer based on user role
        :return:
        """
        user = self.request.user
        if user and user.app_user_type == 'JOIE':
            return TimeSheet_Joie_Serializer
        if user and user.app_user_type == 'Employer':
            return TimeSheet_Emp_Serializer
        else:
            raise PermissionDenied

    def get_queryset(self):
        """
        for joie, archived timesheet means deleted
        :return:
        """
        user = self.request.user
        if user and user.app_user_type == 'JOIE':
            joie = JOIE.objects.get(user=user)
            return TimeSheet.objects.filter(joie=joie).exclude(status__in=['archived'])
        if user and user.app_user_type == 'Employer':
            emp = Employer.objects.get(user=user)
            company = emp.company
            joie_db = CoyJOIEDB.objects.filter(company=company)
            return TimeSheet.objects.filter(coy_joie_db=joie_db, status__in=['pending'])

    def perform_create(self, serializer):
        creator = self.request.user
        if creator and creator.app_user_type == 'JOIE':
            joie = JOIE.objects.get(user=creator)
            feedback = FeedBack.objects.create()     #init an empty feedback
            serializer.save(joie=joie, feedback=feedback)
        else:
            raise PermissionDenied

    def perform_destroy(self, instance):
        """
        will not delete the timesheet object, but update the status to archived
        :param instance:
        :return:
        """
        if instance.status == TimeSheet.STATUS.pending:
            # cannot delete a pending timesheet
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        instance.status = TimeSheet.STATUS.archived
        instance.save()

    @detail_route(methods=['post'])
    def submit(self, request, pk=None):
        """
       joie can submit the draft timesheet

        """
        draft_timesheet = self.get_object()
        serializer = ActionSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.data.pop('action') == AVAILABLE_ACTIONS['TIMESHEET_SUBMIT']:
                if draft_timesheet.status != TimeSheet.STATUS.draft:
                    return Response({'status': 'can only submit draft timesheet'})
                draft_timesheet.status = TimeSheet.STATUS.pending
                draft_timesheet.save()
                return Response({'status': 'timesheet submitted'})
            else:
                return Response({'status': 'action not supported'})
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


class FeedBackViewSet(NestedViewSetMixin, RetrieveUpdateViewSet):
    """
    payed employers can view the details info of the applicants
    """
    serializer_class = FeedbackSerializer
    permission_classes = (
        IsEmployer,
    )
    queryset = FeedBack.objects.all()
    # def get_queryset(self):
    #     user = self.request.user
    #     emp = Employer.objects.get(user=user)
    #     return CoyJOIEDB.objects.filter(company=emp.company)