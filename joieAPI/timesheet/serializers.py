from rest_framework import serializers
from timesheet.models import CoyJOIEDB, TimeSheet, FeedBack
from authentication.serializers import CompanySerializer, JOIEMESerializer
from authentication.models import JOIE, User
from joieAPI.adhoc import ModelChoiceField



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


class TimeSheet_Joie_Serializer(serializers.ModelSerializer):
    # def get_joie_db(self):
    #     user = self.context['request'].user
    #     joie = JOIE.objects.get(user=user)
    #     # return CoyJOIEDB.objects.filter(joie=joie).values_list('company', flat=True)
    #     return CoyJOIEDB.objects.filter(joie=joie)
    # coy_joie_db = ModelChoiceField(choices=get_joie_db())
    # coy_joie_db = serializers.SerializerMethodField('get_joie_db')

    # print coy_joie_db

    # coy_joie_db = ModelChoiceField(choices=joie_db)
    def __init__(self, *args, **kwargs):
        # joie = self.context['request'].user
        # print joie
        # print self.joie_db

        # self.joie_db = None
        super(TimeSheet_Joie_Serializer, self).__init__(*args, **kwargs)
        user = self.context['request'].user
        joie = JOIE.objects.get(user=user)
        # print CoyJOIEDB.objects.filter(joie=joie).values_list('company__name', flat=True)
        # joie_db =
        self.fields['coy_joie_db'] = ModelChoiceField(choices=CoyJOIEDB.objects.filter(joie=joie).values_list('company__name', flat=True))
        # self.coy_joie_db. = ModelChoiceField(CoyJOIEDB.objects.filter(joie=joie).values_list('company__name', flat=True))

    # coy_joie_db = ModelChoiceField(choices=joie_db)
    # coy_joie_db = CoyJOIEDBSerializer(required=False)
    class Meta:
        model = TimeSheet
        extra_kwargs = {'url': {'view_name': 'timesheet-joie-detail'}}
        exclude = ('joie', 'feedback', 'status')
        # include = ('id', 'remark')



    # def get_joie_db(self):
    #     user = self.context['request'].user
    #     joie = JOIE.objects.get(user=user)
    #     return CoyJOIEDB.objects.filter(joie=joie).values_list('company', flat=True)

    def create(self, validated_data):
        joie = validated_data.pop('joie', None)
        coy_joie_db = validated_data.pop('coy_joie_db', None)
        feedback = validated_data.pop('feedback', None)
        timesheet = TimeSheet.objects.create(joie=joie, coy_joie_db=coy_joie_db, feedback=feedback, **validated_data)
        return  timesheet