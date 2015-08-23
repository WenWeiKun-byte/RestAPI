from rest_framework import serializers
from timesheet.models import CoyJOIEDB
from authentication.serializers import CompanySerializer, JOIEMESerializer
from authentication.models import JOIE, User


class CoyJOIEDBSerializer(serializers.HyperlinkedModelSerializer):

    company = serializers.StringRelatedField(read_only=True)  # we need the name only
    joie = serializers.EmailField(required=True)  # joie's email

    class Meta:
        model = CoyJOIEDB
        extra_kwargs = {'url': {'view_name': 'joiedb-detail'}}

    def create(self, validated_data):
        joie_email = validated_data.pop('joie')
        user = None
        try:
            user = User.objects.get(email=joie_email)
        except:
            raise serializers.ValidationError('please input an valid JOIE ID')
        joie = JOIE.objects.get(user=user)
        joiedb = CoyJOIEDB.objects.create(joie=joie, **validated_data)
        return joiedb

    def update(self, instance, validated_data):
        joie_email = validated_data.pop('joie', instance.joie)
        user = None
        try:
            user = User.objects.get(email=joie_email)
        except:
            raise serializers.ValidationError('please input an valid JOIE ID')
        instance.joie = JOIE.objects.get(user=user)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance