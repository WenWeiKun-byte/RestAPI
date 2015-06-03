from rest_framework import generics
from rest_framework import viewsets
from rest_framework.response import Response

from .serializers import EmployerSerializer, EmployeeSerializer
from .models import EmployerProfile, EmployeeProfile


# class EmployerList(generics.ListAPIView):
#     queryset = Account.objects.all()
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
class EmployerViewSet(viewsets.ModelViewSet):
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


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = EmployeeProfile.objects.all()
    serializer_class = EmployeeSerializer