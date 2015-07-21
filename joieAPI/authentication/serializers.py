from rest_framework import serializers
from djoser.serializers import AbstractUserRegistrationSerializer

from .models import JOIE, Employer, User, Industry, Company, SocialLink, Financial
from joieAPI.adhoc import ModelChoiceField, ImageField


class UserRegistrationSerializer(AbstractUserRegistrationSerializer):
    """
    override default registration serializer, separate the the need of REQUIRED_FIELDS
    """
    class Meta(AbstractUserRegistrationSerializer.Meta):
        model = User
        fields = (
            User.USERNAME_FIELD,
            User._meta.pk.name,
            'password',
            'app_user_type',
        )
        write_only_fields = (
            'password',
        )

    def create(self, validated_data):
            return User.objects.create_user(**validated_data)


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
    socialLinks = SocialLinkSerializer(many=True, required=False)

    # required fields
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)

    class Meta:
        model = User
        first_sign_in = serializers.SerializerMethodField(method_name='first_sign_in')

        fields = (
            'email', 'first_name', 'last_name', 'app_user_type', 'socialLinks', 'create_at', 'create_by', 'update_at',
            'update_by', 'last_login', 'first_sign_in', 'status', )
        read_only_fields = (
            'email', 'create_at', 'create_by', 'update_at', 'update_by', 'app_user_type', 'last_login')

    def first_sign_in(self, obj):
        return obj.first_sign_in()

    def update(self, instance, validated_data):
        user = instance
        socialLinks_data = validated_data.pop('socialLinks', None)
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
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AccountMeSerializer(AccountSerializer):
    """
    user cannot update the status by his own
    """
    status = serializers.CharField(read_only=True)


class AccountAdminSerializer(AccountSerializer):
    """
    use by admin users themselves
    """

    class Meta(AccountSerializer.Meta):
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'create_at', 'create_by', 'update_at',
            'update_by', 'last_login')
        read_only_fields = (
            'email', 'create_at', 'create_by', 'update_at', 'update_by', 'last_login')


class IndustrySerializer(serializers.HyperlinkedModelSerializer):
    """
    used by serializer of company
    """

    class Meta:
        model = Industry
        fields = ('url', 'name', 'description')


class CompanySerializer(serializers.ModelSerializer):
    """
    used by serializer of employer
    """

    industry = ModelChoiceField(choices=Industry.objects.all().values_list('name', flat=True))
    logo = ImageField(allow_null=True, required=False)

    # required fields
    name = serializers.CharField(max_length=100, required=True)
    roc = serializers.CharField(max_length=40, required=True)
    business_type = serializers.ChoiceField(choices=[('Direct', 'Direct'), ('Agency', 'Agency')], required=True)
    ea = serializers.CharField(max_length=40, required=True)
    credit_amount = serializers.FloatField(required=True)

    class Meta:
        model = Company

    def get_validation_exclusions(self):
        exclusions = super(CompanySerializer, self).get_validation_exclusions()
        return exclusions + ['postal_code']

    def create(self, validated_data):
        industry_name = validated_data.pop('industry')
        industry = Industry.objects.get(name=industry_name)
        company = Company.objects.create(industry=industry, **validated_data)
        return company

    def update(self, instance, validated_data):
        industry_name = validated_data.pop('industry', instance.industry)
        industry = Industry.objects.get(name=industry_name)
        instance.industry = industry
        # deleting the image because has a None value
        if 'image' in validated_data and not validated_data['image']:
            validated_data.pop('image')
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class CompanyMeSerializer(CompanySerializer):
    # user cannot update the credit_amount by his own.
    credit_amount = serializers.FloatField(read_only=True)


class BaseEmployerSerializer(serializers.HyperlinkedModelSerializer):
    """
    BaseEmployerSerializer for admin user.
    admin user can update all of the necessary fields
    """

    user = AccountSerializer(required=True)
    company = CompanySerializer(required=True)

    class Meta:
        model = Employer

    def update(self, instance, validated_data):
        user_data = validated_data.get('user', None)
        company_data = validated_data.get('company', None)
        if user_data:
            instance.user = AccountSerializer().update(instance.user, user_data)
        if company_data:
            instance.company = CompanySerializer().update(instance.company, company_data)
        instance.save()
        return instance


class EmployerMeSerializer(BaseEmployerSerializer):
    """
    For /me viewset

    """
    user = AccountMeSerializer(required=True)
    company = CompanyMeSerializer(required=True)


class FinancialSerializer(serializers.ModelSerializer):
    """
    used by serializer of joie
    """

    class Meta:
        model = Financial
        fields = ('bank_code', 'branch_code', 'account_number')


class BaseJOIESerializer(serializers.HyperlinkedModelSerializer):
    """
    for super admin user. the admin user cannot update the financial detail
    admin user can update all of the necessary fields
    """
    user = AccountSerializer(required=True)
    financial_detail = FinancialSerializer(required=False)

    # required fields
    nric = serializers.CharField(max_length=20, required=True)
    nric_name = serializers.CharField(max_length=40, required=True)
    nric_type = serializers.ChoiceField(choices=[('Singaporean', 'Singaporean'), ('PR', 'PR')], required=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[(0, 'Male'), (1, 'Female')], required=True)
    contact_number = serializers.CharField(max_length=20, required=True)

    class Meta:
        model = JOIE

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)  # in case of partial update, it could be None
        financial_data = validated_data.pop('financial_detail', None)
        if user_data:
            instance.user = AccountSerializer().update(instance.user, user_data)
        # financial object created during JOIE object creation
        if financial_data:
            instance.financial_detail = FinancialSerializer().update(instance.financial_detail, financial_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class JOIEAdminSerializer(BaseJOIESerializer):
    """
    admin user cannot update the financial detail
    """
    financial_detail = FinancialSerializer(read_only=True)


class JOIEMESerializer(BaseJOIESerializer):
    """
    For /me viewset
    """
    user = AccountMeSerializer(required=True)
    financial_detail = FinancialSerializer(required=False)

    punctuality = serializers.FloatField(read_only=True)
    performance = serializers.FloatField(read_only=True)
    attitude = serializers.FloatField(read_only=True)
    rating = serializers.FloatField(read_only=True)


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

