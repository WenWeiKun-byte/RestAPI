from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from .models import JOIE, Employer, User, Industry, Company, SocialLink, Financial


class SocialLinkSerializer(serializers.ModelSerializer):
    """
    used by serializer of user
    """
    class Meta:
        model = SocialLink
        fields = ('network_name', 'link')


class AccountSerializer(serializers.ModelSerializer):
    """
    first_name and last_name can be updated by user
    """
    socialLinks = SocialLinkSerializer(many=True)

    class Meta:
        model = User
        fields = (
        'email', 'first_name', 'last_name', 'app_user_type', 'socialLinks', 'create_at', 'create_by', 'update_at', 'update_by', )
        read_only_fields = (
        'email', 'create_at', 'create_by', 'update_at', 'update_by', 'app_user_type',)

    def update(self, instance, validated_data):
        user = instance
        socialLinks_data = validated_data.pop('socialLinks')
        if socialLinks_data:
            # user.socialLinks.clear()
            SocialLink.objects.filter(user=user).delete()
            for socialLink_data in socialLinks_data:
                try:
                    socialLink = SocialLink.objects.get(user=user, network_name=socialLink_data['network_name'])
                    socialLink.link = socialLink_data['link']
                    socialLink.save()
                except SocialLink.DoesNotExist:
                    SocialLink.objects.create(user=user, **socialLink_data)
        else:
            # user.socialLinks.clear()
            SocialLink.objects.filter(user=user).delete()
        instance.save()
        return instance


class IndustrySerializer(serializers.HyperlinkedModelSerializer):
    """
    used by serializer of company
    """
    class Meta:
        model = Industry
        fields = ('url', 'name', 'description')


class ModelChoiceField(serializers.ChoiceField):
    def to_representation(self, value):
        if value in ('', None):
            return value
        return value.get_name


class CompanySerializer(serializers.HyperlinkedModelSerializer):
    """
    used by serializer of employer
    """
    industry = ModelChoiceField(choices=Industry.objects.all().values_list('name', flat=True))

    class Meta:
        model = Company

    def create(self, validated_data):
        industry_name = validated_data.pop('industry')
        industry = Industry.objects.get(name=industry_name)
        company = Company.objects.create(industry=industry, **validated_data)
        return company

    def update(self, instance, validated_data):
        industry_name = validated_data.pop('industry')
        industry = Industry.objects.get(name=industry_name)
        instance.industry = industry
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class Employer_For_Admin_Serializer(serializers.HyperlinkedModelSerializer):
    """
    Employer_For_Admin_Serializer for admin user.
    admin user can update all of the necessary fields
    """

    user = AccountSerializer()
    company = CompanySerializer()

    class Meta:
        model = Employer

    def update(self, instance, validated_data):
        user_data = validated_data['user']
        company_data = validated_data['company']
        instance.user = AccountSerializer().update(instance.user, user_data)
        instance.company = CompanySerializer().update(instance.company, company_data)
        instance.save()
        return instance


class FinancialSerializer(serializers.ModelSerializer):
    """
    used by serializer of company
    """
    class Meta:
        model = Financial
        fields = ('bank_number', 'branch_number', 'account_number')


class Employee_For_Admin_Serializer(serializers.HyperlinkedModelSerializer):
    """
    Employee_For_Admin_Serializer for admin user.
    admin user can update all of the necessary fields
    """
    user = AccountSerializer()
    financial_detail = FinancialSerializer()

    class Meta:
        model = JOIE

    def update(self, instance, validated_data):
        user_data = validated_data['user']
        financial_data = validated_data['financial_detail']
        instance.user = AccountSerializer().update(instance.user, user_data)
        # financial object created during JOIE object creation
        instance.financial_detail = FinancialSerializer().update(instance.financial_detail, financial_data)
        instance.save()
        return instance


class Employer_For_Staff_Serializer(serializers.HyperlinkedModelSerializer):
    """
    Employer_For_Staff_Serializer for admin user.
    staff user cannot update the financial details
    """

    user = AccountSerializer()

    class Meta:
        model = Employer
        fields = ('url', 'user', 'company_name', 'roc_number', 'business_type', 'ea_number', 'company_address',
                  'company_postal_code', 'company_description', 'company_contact_person',
                  'company_contact_detail', 'company_logo',
                  'facebook', 'twitter', 'instagram',
                  'status')
        # read_only_fields = ('first_time_sign_in', 'last_edited_by',)    # not expose to endpoint but can update at view

    def update(self, instance, validated_data):
        user_data = validated_data['user']
        print validated_data
        print len(user_data)
        user = instance.user

        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.roc_number = validated_data.get('roc_number', instance.roc_number)
        instance.business_type = validated_data.get('business_type', instance.business_type)
        instance.ea_number = validated_data.get('ea_number', instance.ea_number)
        instance.company_address = validated_data.get('company_address', instance.company_address)
        instance.company_postal_code = validated_data.get('company_postal_code', instance.company_postal_code)
        instance.company_description = validated_data.get('company_description', instance.company_description)
        instance.company_contact_person = validated_data.get('company_contact_person', instance.company_contact_person)
        instance.company_contact_detail = validated_data.get('company_contact_detail', instance.company_contact_detail)
        instance.company_logo = validated_data.get('company_logo', instance.company_logo)

        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.twitter = validated_data.get('twitter', instance.twitter)
        instance.instagram = validated_data.get('instagram', instance.instagram)

        instance.status = validated_data.get('status', instance.status)

        instance.save()

        user.username = user_data.get('username', user.username)
        user.save()

        return instance


class Employee_For_Staff_Serializer(serializers.HyperlinkedModelSerializer):
    """
    Employee_For_Staff_Serializer for admin user.
    staff user cannot update the financial details
    """
    user = AccountSerializer()

    class Meta:
        model = JOIE
        fields = ('url', 'user', 'nric_num', 'name_on_nric', 'nric_type', 'date_of_birth',
                  'preferred_name', 'photo', 'gender',
                  'contact_number', 'block_building', 'street_name', 'unit_number', 'postal_code',
                  'feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude', 'rating',
                  'referred_from',
                  'facebook', 'twitter', 'instagram',
                  'status')
        # read_only_fields = ('first_time_sign_in', 'last_edited_by',)

    def update(self, instance, validated_data):
        user_data = validated_data['user']
        print validated_data
        print len(user_data)
        user = instance.user

        instance.nric_num = validated_data.get('nric_num', instance.nric_num)
        instance.name_on_nric = validated_data.get('name_on_nric', instance.name_on_nric)
        instance.nric_type = validated_data.get('nric_type', instance.nric_type)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.preferred_name = validated_data.get('preferred_name', instance.preferred_name)
        instance.photo = validated_data.get('photo', instance.photo)
        instance.gender = validated_data.get('gender', instance.gender)

        instance.contact_number = validated_data.get('contact_number', instance.contact_number)
        instance.block_building = validated_data.get('block_building', instance.block_building)
        instance.street_name = validated_data.get('street_name', instance.street_name)
        instance.unit_number = validated_data.get('unit_number', instance.unit_number)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)

        instance.feedback_score_punctuality = validated_data.get('feedback_score_punctuality',
                                                                 instance.feedback_score_punctuality)
        instance.feedback_score_job_performance = validated_data.get('feedback_score_job_performance',
                                                                     instance.feedback_score_job_performance)
        instance.feedback_score_attitude = validated_data.get('feedback_score_attitude',
                                                              instance.feedback_score_attitude)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.referred_from = validated_data.get('referred_from', instance.referred_from)

        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.twitter = validated_data.get('twitter', instance.twitter)
        instance.instagram = validated_data.get('instagram', instance.instagram)

        instance.status = validated_data.get('status', instance.status)

        instance.save()

        user.username = user_data.get('username', user.username)
        user.save()

        return instance


class Employer_For_User_Serializer(serializers.HyperlinkedModelSerializer):
    """
    for /me url use
    user can update their necessary information here
    """

    class Meta:
        model = Employer
        fields = ('company_name', 'roc_number', 'business_type', 'ea_number', 'company_address',
                  'company_postal_code', 'company_description', 'company_contact_person',
                  'company_contact_detail', 'company_logo',
                  'facebook', 'twitter', 'instagram',
                  'status'
                  )
        read_only_fields = ('status',)


class Employee_For_User_Serializer(serializers.HyperlinkedModelSerializer):
    """
    for /me url use
    user can update their necessary information here
    """

    class Meta:
        model = JOIE
        fields = ('nric_num', 'name_on_nric', 'nric_type', 'date_of_birth',
                  'preferred_name', 'photo', 'gender',
                  'contact_number', 'block_building', 'street_name', 'unit_number', 'postal_code',
                  'feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude', 'rating',
                  'referred_from',
                  'facebook', 'twitter', 'instagram',
                  'status'
                  )
        read_only_fields = ('feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude',
                            'rating', 'status')


class Account_Employer_Serializer(serializers.HyperlinkedModelSerializer):
    """
    for /me url use
    user can update their necessary information here
    """
    employer_profile = Employer_For_User_Serializer()

    class Meta:
        model = User
        fields = (
        'email', 'username', 'created_at', 'updated_at', 'last_login', 'app_user_type', 'first_time_sign_in',
        'last_edited_by', 'employer_profile')
        read_only_fields = (
        'email', 'created_at', 'updated_at', 'last_login', 'app_user_type', 'first_time_sign_in', 'last_edited_by')

    def update(self, instance, validated_data):
        profile_data = validated_data['employer_profile']
        profile = instance.employer_profile

        instance.username = validated_data.get('username', instance.username)
        instance.last_edited_by = validated_data.get('last_edited_by', instance.last_edited_by)
        instance.save()

        profile.company_name = profile_data.get('company_name', profile.company_name)
        profile.roc_number = profile_data.get('roc_number', profile.roc_number)
        profile.business_type = profile_data.get('business_type', profile.business_type)
        profile.ea_number = profile_data.get('ea_number', profile.ea_number)
        profile.company_address = profile_data.get('company_address', profile.company_address)
        profile.company_postal_code = profile_data.get('company_postal_code', profile.company_postal_code)
        profile.company_description = profile_data.get('company_description', profile.company_description)
        profile.company_contact_person = profile_data.get('company_contact_person', profile.company_contact_person)
        profile.company_contact_detail = profile_data.get('company_contact_detail', profile.company_contact_detail)
        profile.company_logo = profile_data.get('company_logo', profile.company_logo)
        profile.facebook = profile_data.get('facebook', profile.facebook)
        profile.twitter = profile_data.get('twitter', profile.twitter)
        profile.instagram = profile_data.get('instagram', profile.instagram)
        profile.status = profile_data.get('status', profile.status)

        profile.save()

        return instance


class Account_Employee_Serializer(serializers.HyperlinkedModelSerializer):
    """
    for /me url use
    user can update their necessary information here
    """
    employee_profile = Employee_For_User_Serializer()

    class Meta:
        model = User
        fields = (
        'email', 'username', 'created_at', 'updated_at', 'last_login', 'app_user_type', 'first_time_sign_in',
        'last_edited_by', 'employee_profile')
        read_only_fields = (
        'email', 'created_at', 'updated_at', 'last_login', 'app_user_type', 'first_time_sign_in', 'last_edited_by')

    def update(self, instance, validated_data):
        profile_data = validated_data['employee_profile']
        profile = instance.employee_profilel

        instance.username = validated_data.get('username', instance.username)
        instance.last_edited_by = validated_data.get('last_edited_by', instance.last_edited_by)
        instance.save()

        profile.nric_num = profile_data.get('nric_num', profile.nric_num)
        profile.name_on_nric = profile_data.get('name_on_nric', profile.name_on_nric)
        profile.nric_type = profile_data.get('nric_type', profile.nric_type)
        profile.date_of_birth = profile_data.get('date_of_birth', profile.date_of_birth)
        profile.preferred_name = profile_data.get('preferred_name', profile.preferred_name)
        profile.photo = profile_data.get('photo', profile.photo)
        profile.gender = profile_data.get('gender', profile.gender)
        profile.contact_number = profile_data.get('contact_number', profile.contact_number)
        profile.block_building = profile_data.get('block_building', profile.block_building)
        profile.street_name = profile_data.get('street_name', profile.street_name)
        profile.unit_number = profile_data.get('unit_number', profile.unit_number)
        profile.postal_code = profile_data.get('postal_code', profile.postal_code)
        profile.referred_from = profile_data.get('referred_from', profile.referred_from)
        profile.facebook = profile_data.get('facebook', profile.facebook)
        profile.twitter = profile_data.get('twitter', profile.twitter)
        profile.instagram = profile_data.get('instagram', profile.instagram)
        profile.status = profile_data.get('status', profile.status)

        profile.save()

        return instance


class StaffRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            User.USERNAME_FIELD,
            User._meta.pk.name,
            'password',
        )
        write_only_fields = (
            'password',
        )

    def create(self, validated_data):
        return User.objects.create_admin(**validated_data)