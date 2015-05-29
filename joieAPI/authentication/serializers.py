from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from .models import EmployeeProfile, EmployerProfile, Account


class EmployerProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmployerProfile
        fields = ('company_name', 'roc_number', 'business_type', 'company_address',
                  'company_postal_code', 'company_description', 'company_contact_person',
                  'company_contact_detail', 'company_logo',
                  'credit_amount', 'card_type', 'card_number', 'name_on_card', 'expiration_date',
                  'card_security_code', 'billing_address', 'city', 'state_province', 'zip_code', 'billing_email',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
        read_only_fields = ('first_time_sign_in', 'last_edited_by',)


class EmployeeProfileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmployeeProfile
        fields = ('nric_num', 'name_on_nric', 'nric_type', 'date_of_birth',
                  'preferred_name', 'photo', 'gender',
                  'contact_number', 'block_building', 'street_name', 'unit_number', 'postal_code',
                  'bank_number', 'branch_number', 'account_number',
                  'feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude', 'rating',
                  'referred_from',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
        read_only_fields = ('first_time_sign_in', 'last_edited_by',)


class EmployerSerializer(serializers.HyperlinkedModelSerializer):
    employer_profile = EmployerProfileSerializer()

    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'created_at', 'updated_at', 'app_user_type', 'employer_profile')
        read_only_fields = ('email', 'created_at', 'updated_at', 'app_user_type')


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    employee_profile = EmployeeProfileSerializer()

    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'created_at', 'updated_at', 'app_user_type', 'employee_profile')
        read_only_fields = ('email', 'created_at', 'updated_at', 'app_user_type')