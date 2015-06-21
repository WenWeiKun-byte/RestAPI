import json
from django.http import HttpResponse
from rest_framework import filters
from rest_framework import viewsets
from rest_framework import mixins, generics, permissions
from rest_framework.test import APIClient
from rest_framework.exceptions import PermissionDenied

from .serializers import Employee_For_Admin_Serializer, Employee_For_Staff_Serializer, AccountSerializer, \
    Employer_For_Admin_Serializer, Employer_For_Staff_Serializer, Account_Employee_Serializer, \
    Account_Employer_Serializer, StaffRegistrationSerializer, IndustrySerializer, CompanySerializer
from .models import Employer, JOIE, User, Industry, Company
from .permissions import IsAdmin, IsSuperAdmin


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

def activate(request, uid, token):
    client = APIClient(enforce_csrf_checks=True)
    response = client.post('/auth/activate/', {'uid': uid, 'token': token})
    r = json.loads(response.content)
    if 'auth_token' in r.keys():
        return HttpResponse('account activated')
    else:
        return HttpResponse('account activated fail')


class IndustryViewSet(viewsets.ModelViewSet):
    """
    this view set is used by admin user for Industry models management
    """
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all()


class CompanyViewSet(viewsets.ModelViewSet):
    """
    for test only
    """
    serializer_class = CompanySerializer
    queryset = Company.objects.all()


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
    queryset = Employer.objects.all()

    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('status', 'user__username')
    search_fields = ('user__username', 'user__email')

    def get_serializer_class(self):
        if self.request.user.is_staff:
            if self.request.user.is_admin:
                return Employer_For_Admin_Serializer
            return Employer_For_Staff_Serializer
        else:
            raise PermissionDenied

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save()
        instance.user.last_edited_by = user.email
        serializer.save()
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
    queryset = JOIE.objects.all()

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_serializer_class(self):
        if self.request.user.is_staff:
            if self.request.user.is_admin:
                return Employee_For_Admin_Serializer
            return Employee_For_Staff_Serializer
        else:
            raise PermissionDenied

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save()
        instance.user.last_edited_by = user.email
        serializer.save()
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
                     ]
        if instance.status == '1' and all(checklist):
            serializer.save(status='2')  # completed Profile
        if instance.status == '2' and not all(checklist):
            serializer.save(status='1')  # completed Profile


class UserView(generics.RetrieveUpdateAPIView):
    """
    override /me Use this endpoint to retrieve/update user.
    """
    model = User
    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get_object(self, *args, **kwargs):
        obj = self.request.user
        self.check_object_permissions(self.request, obj)
        return obj

    def get_serializer_class(self):
        obj = self.request.user
        if obj.app_user_type == 'Employer':
            return Account_Employer_Serializer
        if obj.app_user_type == 'Employee':
            return Account_Employee_Serializer
        return AccountSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save(last_edited_by=user.email)
        if user.app_user_type == 'Employee':
            checklist = [instance.employee_profile.nric_num is not '',
                         instance.employee_profile.name_on_nric is not '',
                         instance.employee_profile.nric_type is not '',
                         instance.employee_profile.date_of_birth is not '',
                         instance.employee_profile.preferred_name is not None,
                         instance.employee_profile.photo is not '',
                         instance.employee_profile.gender is not '',
                         instance.employee_profile.contact_number is not '',
                         instance.employee_profile.block_building is not '',
                         instance.employee_profile.street_name is not '',
                         instance.employee_profile.unit_number is not '',
                         instance.employee_profile.postal_code is not None,
                         ]
            if instance.employee_profile.status == '1' and all(checklist):
                instance.employer_profile.status = '2'
                serializer.save()  # completed Profile
            if instance.employee_profile.status == '2' and not all(checklist):
                instance.employer_profile.status = '1'
                serializer.save()  # completed Profile
        if user.app_user_type == 'Employer':
            checklist = [instance.employer_profile.company_name is not '',
                         instance.employer_profile.roc_number is not '',
                         instance.employer_profile.business_type is not '',
                         instance.employer_profile.company_address is not '',
                         instance.employer_profile.company_postal_code is not None,
                         instance.employer_profile.company_contact_person is not '',
                         instance.employer_profile.company_contact_detail is not '',
                         instance.employer_profile.company_logo is not '',
                         ]
            if instance.employer_profile.status == '1' and all(checklist):
                instance.employer_profile.status = '2'
                serializer.save()  # completed Profile
            if instance.employer_profile.status == '2' and not all(checklist):
                instance.employer_profile.status = '1'
                serializer.save()  # completed Profile


class StaffRegistrationView(generics.CreateAPIView):
    """
    this view used for admin user to create staff users
    """
    model = User
    permission_classes = (
        permissions.IsAuthenticated,
        IsSuperAdmin
    )
    serializer_class = StaffRegistrationSerializer
