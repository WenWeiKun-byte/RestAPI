from rest_framework import serializers
from timesheet.models import CoyJOIEDB, TimeSheet, FeedBack
from authentication.serializers import CompanySerializer, JOIEMESerializer
from authentication.models import JOIE, User, Company
from joieAPI.adhoc import ModelChoiceField
from authentication.serializers import BaseJOIESerializer


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeedBack

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


class TimeSheet_Joie_Serializer(serializers.HyperlinkedModelSerializer):

    feedback = FeedbackSerializer(required=False)

    def __init__(self, *args, **kwargs):

        super(TimeSheet_Joie_Serializer, self).__init__(*args, **kwargs)
        user = self.context['request'].user
        joie = JOIE.objects.get(user=user)

        self.fields['coy_joie_db'] = ModelChoiceField(choices=CoyJOIEDB.objects.filter(joie=joie).values_list('company__name', flat=True))

    class Meta:
        model = TimeSheet
        extra_kwargs = {'url': {'view_name': 'timesheet-joie-detail'}}
        exclude = ('joie', )
        read_only_fields = ('status', 'feedback')

    def create(self, validated_data):
        joie = validated_data.pop('joie', None)
        company_name = validated_data.pop('coy_joie_db', None)  # we provide the company name for use to choice
        company = Company.objects.get(name=company_name)
        coy_joie_db = CoyJOIEDB.objects.get(joie=joie, company=company)
        feedback = validated_data.pop('feedback', None)
        timesheet = TimeSheet.objects.create(joie=joie, coy_joie_db=coy_joie_db, feedback=feedback, **validated_data)
        return timesheet

    def update(self, instance, validated_data):
        """
        use can only update the draft timesheet;
        timesheet that have submitted cannot change
        :param instance:
        :param validated_data:
        :return:
        """
        timesheet = instance
        if timesheet.status != TimeSheet.STATUS.draft:
            raise serializers.ValidationError('only draft timesheet can be updated')
        company_name = validated_data.pop('coy_joie_db', None)
        if company_name:
            company = Company.objects.get(name=company_name)
            coy_joie_db = CoyJOIEDB.objects.get(joie=instance.joie, company=company)
            timesheet.coy_joie_db = coy_joie_db
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TimeSheet_Emp_Serializer(serializers.HyperlinkedModelSerializer):

    joie = BaseJOIESerializer(required=False)

    class Meta:
        """
        emp
        can modify clock_in,clock_out,break_duration

        """
        model = TimeSheet
        extra_kwargs = {'url': {'view_name': 'timesheet-joie-detail'}}
        exclude = ('status', 'feedback', 'coy_joie_db')
        read_only_fields = ('remarks', 'joie',)