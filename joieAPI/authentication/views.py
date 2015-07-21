import json
from django.http import HttpResponse
from rest_framework import filters, response, status
from rest_framework import viewsets
from rest_framework import mixins, generics, permissions
from rest_framework.test import APIClient
from rest_framework.exceptions import PermissionDenied
from djoser import utils
from djoser.serializers import PasswordRetypeSerializer
from djoser.views import RegistrationView

from .serializers import AccountAdminSerializer, BaseJOIESerializer, JOIEAdminSerializer, \
    BaseEmployerSerializer, EmployerMeSerializer, JOIEMESerializer, \
    UserRegistrationSerializer, StaffRegistrationSerializer, IndustrySerializer
from .models import Employer, JOIE, User, Industry, Company
from .permissions import IsActiveUser, IsSuperAdmin, IsAccountOwner, IsAdmin, IsAvailableUser


USER_TYPE = {'JOIE': 'JOIE', 'EMPLOYER': 'Employer'}


def activate(request, uid, token):
    client = APIClient(enforce_csrf_checks=True)
    response = client.post('/auth/activate/', {'uid': uid, 'token': token})
    r = json.loads(response.content)
    if 'auth_token' in r.keys():
        return HttpResponse('account activated')
    else:
        return HttpResponse('account activated fail')


class UserRegistrationView(RegistrationView):
    def get_serializer_class(self):
        return UserRegistrationSerializer


class ResetConfirmView(utils.ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to change user password.
    """

    def get_serializer_class(self):
        return PasswordRetypeSerializer

    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.DATA)
        if serializer.is_valid():
            return self.action(serializer, **kwargs)
        else:
            return response.Response(
                data=serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

    def action(self, serializer, **kwargs):
        uid = kwargs.get('uid')
        token = kwargs.get('token')
        pwd = serializer.data['new_password']
        client = APIClient(enforce_csrf_checks=True)
        r = client.post('/auth/password/reset/confirm/', {'uid': uid, 'token': token, 'new_password': pwd, 're_new_password': pwd})
        if r:
            return HttpResponse('password reset failed - %s' % json.loads(r.content))
        else:
            return HttpResponse('password reset succeed')

class IndustryViewSet(viewsets.ModelViewSet):
    """
    this view set is used by admin user for Industry models management
    """
    permission_classes = (
        IsAdmin,
    )
    serializer_class = IndustrySerializer
    queryset = Industry.objects.all()


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

    queryset = Employer.objects.all()

    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('user__status', 'user__first_time_sign_in')
    search_fields = ('user__last_name', 'user__email')

    def get_serializer_class(self):
        if self.request.user.is_admin:
            if self.request.user.is_superAdmin:
                return BaseEmployerSerializer
            return BaseEmployerSerializer
        else:
            raise PermissionDenied

    def perform_destroy(self, instance):
        """
        will not delete the user object, but update the status to deleted
        :param instance: current user
        :return:
        """
        instance.stats = User.STATUS.deleted
        instance.save()


class EmployeeViewSet(NoCreateViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = JOIE.objects.all()

    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, )
    filter_fields = ('user__status', 'user__first_time_sign_in')
    search_fields = ('user__last_name', 'user__email')

    def get_serializer_class(self):
        if self.request.user.is_admin:
            if self.request.user.is_superAdmin:
                return BaseJOIESerializer
            return JOIEAdminSerializer
        else:
            raise PermissionDenied

    def perform_destroy(self, instance):
        """
        will not delete the user object, but update the status to deleted
        :param instance: current user
        :return:
        """
        instance.stats = User.STATUS.deleted
        instance.save()


class UserView(generics.RetrieveUpdateAPIView):
    """
    override /me Use this endpoint to retrieve/update user.
    """

    permission_classes = (
        permissions.IsAuthenticated,
        IsAvailableUser,
        IsAccountOwner
    )

    def get_object(self, *args, **kwargs):
        account = self.request.user
        obj = None
        self.check_object_permissions(self.request, account)
        if account.app_user_type == USER_TYPE['EMPLOYER']:
            obj = Employer.objects.get(user=account)
        elif account.app_user_type == USER_TYPE['JOIE']:
            obj = JOIE.objects.get(user=account)
        else:
            obj = account
        return obj

    def get_serializer_class(self):
        obj = self.request.user
        if obj.app_user_type == USER_TYPE['EMPLOYER']:
            return EmployerMeSerializer
        if obj.app_user_type == USER_TYPE['JOIE']:
            return JOIEMESerializer
        return AccountAdminSerializer

    def perform_update(self, serializer):
        user = self.request.user
        instance = serializer.save()
        if isinstance(instance, Employer) or isinstance(instance, JOIE):
            instance.user.update_by = user.email
        # if all the required fields updated, change status from inactive to completed_profile
            if self.request.method == 'PUT' and int(instance.user.status) == User.STATUS.inactive:
                instance.user.status = User.STATUS.completed_profile
            if instance.user.first_time_sign_in:
                instance.user.first_time_sign_in = False  # change the first time sign in flag
        else:
            serializer.save(update_by=user.email)
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

    def perform_create(self, serializer):
        creator = self.request.user.email
        serializer.save(create_by=creator)

