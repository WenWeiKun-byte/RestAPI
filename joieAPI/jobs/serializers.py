from rest_framework import serializers, validators
from jobs.models import Job, JobListType, Application
from authentication.models import Employer, JOIE
from datetime import date

from authentication.serializers import EmployerMeSerializer
from joieAPI.adhoc import ModelChoiceField, ImageField, ReadDestroyViewSet


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
    # owner = EmployerMeSerializer(read_only=True)  # no need detail infos
    owner = serializers.StringRelatedField()
    job_list_type = ModelChoiceField(choices=JobListType.objects.all().values_list('list_type', flat=True))
    promotion_banner = ImageField(allow_null=True, required=False)

    class Meta:
        model = Job
        extra_kwargs = {'url': {'view_name': 'job_draft-detail'}}
        exclude = ('applicants', 'job_id', 'status', 'time_of_published')
        read_only_fields = ('owner', 'create_at', 'create_by', 'update_at', 'update_by')

    def create(self, validated_data):
        if validated_data.get('time_of_release') < date.today():
            raise serializers.ValidationError('the release date must be today or a future date')
        job_type_name = validated_data.pop('job_list_type')
        job_list_type = JobListType.objects.get(list_type=job_type_name)
        owner_user = validated_data.pop('owner_user')
        owner = Employer.objects.get(user=owner_user)
        job = Job.objects.create(owner=owner, job_list_type=job_list_type, **validated_data)
        return job

    def update(self, instance, validated_data):
        job_type_name = validated_data.pop('job_list_type', None)
        if job_type_name:
            job_list_type = JobListType.objects.get(list_type=job_type_name)
            instance.job_list_type = job_list_type
        # deleting the image because has a None value
        if 'image' in validated_data and not validated_data['image']:
            validated_data.pop('image')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class JobActiveSerializer(serializers.HyperlinkedModelSerializer):
    """
    Manage the published jobs
    Modify by Employers
    Including copy as draft for an existing job, remove job to archive folder, view job applicants, approval
    """
    owner = serializers.StringRelatedField()
    job_list_type = serializers.SlugRelatedField(read_only=True, slug_field='description')
    applicants = serializers.SerializerMethodField(method_name='get_application_number')

    class Meta:
        model = Job
        extra_kwargs = {'url': {'view_name': 'job_active-detail'}}
        exclude = ('create_at', 'create_by', 'update_at', 'update_by', 'status')
        read_only_fields = ('owner', 'applicants', 'time_of_published', 'time_of_release')

    def get_application_number(self, obj):
        return obj.get_applicant_number()


class JobSerializer(serializers.HyperlinkedModelSerializer):
    """
    Jobs expose to joie
    """
    owner = serializers.StringRelatedField()
    job_list_type = serializers.SlugRelatedField(read_only=True, slug_field='description')
    applicants = serializers.SerializerMethodField(method_name='get_application_number')

    class Meta:
        model = Job
        exclude = ('create_at', 'create_by', 'update_at', 'update_by', 'status')
        read_only_fields = ('owner', 'applicants', 'time_of_published', 'time_of_release')

    def get_application_number(self, obj):
        return obj.get_applicant_number()


class ApplicationEmpSerializer(serializers.ModelSerializer):
    """
    application management for employer
    """
    applicant = serializers.StringRelatedField()

    class Meta:
        model = Application
        extra_kwargs = {'url': {'view_name': 'application-detail'}}
        exclude = ('job',)
        read_only_fields = ('applicant', 'time_of_apply', 'status')


class ApplicationJOIESerializer(serializers.ModelSerializer):
    """
    application management for JOIE
    JOIE may cancel the pending status jobs
    """
    job = JobSerializer(read_only=True)

    class Meta:
        model = Application
        extra_kwargs = {'url': {'view_name': 'joie_application-detail'}}
        exclude = ('applicant',)
        read_only_fields = ('applicant', 'time_of_apply', 'status')




