from rest_framework import serializers, validators
from jobs.models import Job, JobListType, Application, SupportImage
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


class SupportImageSerializer(serializers.ModelSerializer):
    image_1 = ImageField(allow_null=True, required=False)
    image_2 = ImageField(allow_null=True, required=False)
    image_3 = ImageField(allow_null=True, required=False)
    image_4 = ImageField(allow_null=True, required=False)
    image_5 = ImageField(allow_null=True, required=False)
    image_6 = ImageField(allow_null=True, required=False)

    class Meta:
        model = SupportImage


class JobDraftSerializer(serializers.HyperlinkedModelSerializer):
    """
    Created by Employers
    A job listing created by employers to allow JOIEs to apply
    """
    # owner = EmployerMeSerializer(read_only=True)  # no need detail infos
    owner = serializers.StringRelatedField()
    job_list_type = ModelChoiceField(choices=JobListType.objects.all().values_list('list_type', flat=True))
    promotion_banner = ImageField(allow_null=True, required=False)
    support_image = SupportImageSerializer(required=False)

    class Meta:
        model = Job
        extra_kwargs = {'url': {'view_name': 'job_draft-detail'}}
        exclude = ('applicants', 'job_id', 'status', 'time_of_publish')
        read_only_fields = ('owner', 'create_at', 'create_by', 'update_at', 'update_by')

    def create(self, validated_data):
        support_images = validated_data.pop('support_image', None)
        time_of_release = validated_data.get('time_of_release', None)
        if time_of_release is not None and time_of_release < date.today():
            raise serializers.ValidationError('the release date must be today or a future date')
        job_type_name = validated_data.pop('job_list_type')
        job_list_type = JobListType.objects.get(list_type=job_type_name)
        owner_user = validated_data.pop('owner_user')
        owner = Employer.objects.get(user=owner_user)
        job = Job.objects.create(owner=owner, job_list_type=job_list_type, **validated_data)
        if support_images:
            # if len(support_images) > 6:
            #     raise serializers.ValidationError('May upload up to 6 support images')
            # for support_image in support_images:
            #     SupportImage.objects.create(job=job, **support_image)
            job.support_image = SupportImage.objects.create(**support_images)
            job.save()

        return job

    def update(self, instance, validated_data):
        job = instance
        job_type_name = validated_data.pop('job_list_type', None)
        time_of_release = validated_data.get('time_of_release', None)
        # support_images = validated_data.pop('support_image', 'empty')
        support_images = validated_data.pop('support_image', None)
        # if support_images and support_images != 'empty':
        #     SupportImage.objects.filter(job=job).delete()
        #     if len(support_images) > 6:
        #         raise serializers.ValidationError('May upload up to 6 support images')
        #     for support_image_data in support_images:
        #         SupportImage.objects.create(job=job, **support_image_data)
        # elif support_images != 'empty':
        #     # got the key and the value is null, means the use want to remove the values
        #     SupportImage.objects.filter(job=job).delete()
        if support_images:
            job.support_image = SupportImageSerializer().update(instance.support_image, support_images)
        if time_of_release is not None and time_of_release < date.today():
            raise serializers.ValidationError('the release date must be today or a future date')
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
    support_image = SupportImageSerializer(required=False)

    class Meta:
        model = Job
        extra_kwargs = {'url': {'view_name': 'job_active-detail'}}
        exclude = ('create_at', 'create_by', 'update_at', 'update_by', 'status')
        read_only_fields = ('owner', 'applicants', 'time_of_publish', 'time_of_release')

    def get_application_number(self, obj):
        return obj.get_applicant_number()


class JobSerializer(serializers.HyperlinkedModelSerializer):
    """
    Jobs expose to joie
    """
    # owner = serializers.StringRelatedField()
    owner = EmployerMeSerializer(read_only=True)
    job_list_type = serializers.SlugRelatedField(read_only=True, slug_field='description')
    applicants = serializers.SerializerMethodField(method_name='get_application_number')
    job_rate = serializers.SerializerMethodField()
    support_image = SupportImageSerializer(required=False)

    class Meta:
        model = Job
        exclude = ('create_at', 'create_by', 'update_at', 'update_by', 'status')
        read_only_fields = ('owner', 'applicants', 'time_of_publish', 'time_of_release', 'job_rate')

    def get_application_number(self, obj):
        return obj.get_applicant_number()

    def get_job_rate(self, obj):
        return obj.get_job_rate()



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




