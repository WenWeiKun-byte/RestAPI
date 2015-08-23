from timesheet.serializers import CoyJOIEDBSerializer
from timesheet.models import CoyJOIEDB
from rest_framework import viewsets
from authentication.permissions import IsEmployer
from authentication.models import Employer


# Create your views here
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