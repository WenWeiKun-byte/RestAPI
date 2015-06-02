from rest_framework import generics
from rest_framework.response import Response

from .serializers import EmployerSerializer, EmployeeSerializer
from .models import Account


class EmployerList(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = EmployerSerializer


class EmployerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = EmployerSerializer


class EmployeeList(generics.ListAPIView):
    queryset = Account.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = EmployeeSerializer