from rest_framework import serializers
from jobs.models import Job, JobListType, Application

from authentication.serializers import ModelChoiceField


class JobListTypeSerializer(serializers.HyperlinkedModelSerializer):
    """
    pre-created models;
    Chosen during the job creation process
    """
    class Meta:
        model = JobListType


# class JobCreateSerializer(serializers.HyperlinkedModelSerializer):
#     """
#     Created by Employers
#     A job listing created by employers to allow JOIEs to apply
#     """
#     owner = serializers.SlugRelatedField(read_only=True,
#                                          slug_field='company__company_name')
#     job_list_type = ModelChoiceField(choices=JobListType.objects.all().values_list('list_type', flat=True))
#
#
#     class Meta:
#         model = Job
#         exclude = ('applicants',)
#
#     def create(self, validated_data):
#         industry_name = validated_data.pop('industry')
#         industry = Industry.objects.get(name=industry_name)
#         company = Company.objects.create(industry=industry, **validated_data)
#         return company
#
#     def update(self, instance, validated_data):
#         industry_name = validated_data.pop('industry')
#         industry = Industry.objects.get(name=industry_name)
#         instance.industry = industry
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#         return instance
#
#
# class JobListSerializer(serializers.HyperlinkedModelSerializer):
#     pass

