import django_filters
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import mixins

from .serializers import EmployerSerializer, EmployeeSerializer
from .models import EmployerProfile, EmployeeProfile


# class EmployerList(generics.ListAPIView):
# queryset = Account.objects.all()
#     serializer_class = EmployerSerializer
#
#
# class EmployerDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = EmployerSerializer
#
#
# class EmployeeList(generics.ListAPIView):
#     queryset = Account.objects.all()
#     serializer_class = EmployeeSerializer
#
#
# class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Account.objects.all()
#     serializer_class = EmployeeSerializer
# =============use viewset


class NoCreateViewSet(mixins.ListModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    """
    A viewset that provides without 'create' actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """
    pass


class EmployerViewSet(NoCreateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    # def partial_update(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     serializer = self.serialize(instance, data=request.data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     new_instance = serializer.save()
    #     return Response(serializer.data)
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerSerializer

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('status', 'user__username')
    search_fields = ('user__username', 'user__email')

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save(last_edited_by=user.email)
        checklist = [instance.company_name is not '',
                     instance.roc_number is not '',
                     instance.business_type is not '',
                     instance.company_address is not '',
                     instance.company_postal_code is not None,
                     instance.company_contact_person is not '',
                     instance.company_contact_detail is not '',
                     instance.company_logo is not '',
                     ]
        if instance.status == '1' and all(checklist):
            serializer.save(status='2')  # completed Profile
        if instance.status == '2' and not all(checklist):
            serializer.save(status='1')  # completed Profile




class EmployeeViewSet(NoCreateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save(last_edited_by=user.email)
        checklist = [instance.nric_num is not '',
                     instance.name_on_nric is not '',
                     instance.nric_type is not '',
                     instance.date_of_birth is not '',
                     instance.preferred_name is not None,
                     instance.photo is not '',
                     instance.gender is not '',
                     instance.contact_number is not '',
                     instance.block_building is not '',
                     instance.street_name is not '',
                     instance.unit_number is not '',
                     instance.postal_code is not None,
                     instance.bank_number is not '',
                     instance.branch_number is not '',
                     instance.account_number is not '',
                     ]
        if instance.status == '1' and all(checklist):
            serializer.save(status='2')  # completed Profile
        if instance.status == '2' and not all(checklist):
            serializer.save(status='1')  # completed Profile