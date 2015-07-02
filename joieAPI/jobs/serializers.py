from rest_framework import serializers, validators
from jobs.models import Job, JobListType, Application
from authentication.models import Employer, JOIE

from authentication.serializers import ModelChoiceField


class JobListTypeSerializer(serializers.Serializer):
    """
    pre-created models;
    Chosen during the job creation process
    """
    url = serializers.HyperlinkedIdentityField(view_name='joblisttype-detail')
    list_type = serializers.ChoiceField(choices=[(1, 'Normal'), (2, 'Premium Advert'), (3, 'Last Minute Advert')],
                                        validators=[validators.UniqueValidator(queryset=JobListType.objects.all())])
    description = serializers.CharField(allow_blank=True, required=False, style={'base_template': 'textarea.html'})

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

    def create(self, validated_data):
        ModelClass = self.Meta.model
        return ModelClass.objects.create(**validated_data)

    class Meta:
        model = JobListType


class JobDraftSerializer(serializers.HyperlinkedModelSerializer):
    """
    Created by Employers
    A job listing created by employers to allow JOIEs to apply
    """
    owner = serializers.SlugRelatedField(slug_field='company__company_name', read_only=True)
    job_list_type = ModelChoiceField(choices=JobListType.objects.all().values_list('list_type', flat=True))

    class Meta:
        model = Job
        exclude = ('applicants', 'job_id', 'status', 'time_of_published')
        read_only_fields = ('owner', 'create_at', 'create_by', 'update_at', 'update_by')

    def create(self, validated_data):
        job_type_name = validated_data.pop('job_list_type')
        job_list_type = JobListType.objects.get(list_type=job_type_name)
        owner_id = validated_data.pop('owner')
        owner = Employer.objects.get(id=owner_id)
        job = Job.objects.create(owner=owner, job_list_type=job_list_type, **validated_data)
        return job

    def update(self, instance, validated_data):
        job_type_name = validated_data.pop('job_list_type')
        job_list_type = JobListType.objects.get(name=job_type_name)
        instance.job_list_type = job_list_type
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class JobListSerializer(serializers.HyperlinkedModelSerializer):
    pass

