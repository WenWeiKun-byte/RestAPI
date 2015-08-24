from timesheet.serializers import CoyJOIEDBSerializer, TimeSheet_Joie_Serializer
from timesheet.models import CoyJOIEDB, TimeSheet, FeedBack
from rest_framework import viewsets
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
        return TimeSheet.objects.filter(joie=joie)

    def perform_create(self, serializer):
        creator = self.request.user
        joie = JOIE.objects.get(user=creator)
        status = TimeSheet.STATUS.pending
        feedback = FeedBack.object.create()     #init an empty feedback
        serializer.save(joie=joie, status=status, feedback=feedback)