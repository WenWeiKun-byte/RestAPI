from timesheet.serializers import CoyJOIEDBSerializer, TimeSheet_Joie_Serializer
from timesheet.models import CoyJOIEDB, TimeSheet, FeedBack
from rest_framework import viewsets, status
from rest_framework.response import Response
from authentication.permissions import IsEmployer, IsJOIE
from authentication.models import Employer, JOIE


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


class Joie_Timesheet_ViewSet(viewsets.ModelViewSet):

    serializer_class = TimeSheet_Joie_Serializer

    permission_classes = (
        IsJOIE,
    )

    # def get_serializer(self, *args, **kwargs):
    #     user = self.request.user
    #     joie = JOIE.objects.get(user=user)
    #     return TimeSheet_Joie_Serializer

    def get_queryset(self):
        user = self.request.user
        joie = JOIE.objects.get(user=user)
        return TimeSheet.objects.filter(joie=joie).exclude(status__in=['archived'])

    def perform_create(self, serializer):
        creator = self.request.user
        joie = JOIE.objects.get(user=creator)
        feedback = FeedBack.objects.create()     #init an empty feedback
        serializer.save(joie=joie, feedback=feedback)

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