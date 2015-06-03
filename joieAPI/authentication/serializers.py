from django.contrib.auth import update_session_auth_hash

from rest_framework import serializers

from .models import EmployeeProfile, EmployerProfile, Account


class AccountSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Account
        fields = ('id', 'email', 'username', 'created_at', 'updated_at', 'app_user_type', )
        read_only_fields = ('email', 'created_at', 'updated_at', 'app_user_type')


class EmployerSerializer(serializers.HyperlinkedModelSerializer):
    user = AccountSerializer()

    class Meta:
        model = EmployerProfile
        fields = ('user', 'company_name', 'roc_number', 'business_type', 'company_address',
                  'company_postal_code', 'company_description', 'company_contact_person',
                  'company_contact_detail', 'company_logo',
                  'credit_amount', 'card_type', 'card_number', 'name_on_card', 'expiration_date',
                  'card_security_code', 'billing_address', 'city', 'state_province', 'zip_code', 'billing_email',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
        read_only_fields = ('first_time_sign_in', 'last_edited_by',)
        extra_kwargs = {'facebook': {'required': False},
                        'status': {'read_only': True}}

    def update(self, instance, validated_data):
        user_data = validated_data['user']
        print validated_data
        print len(user_data)
        user = instance.user

        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.roc_number = validated_data.get('roc_number', instance.roc_number)
        instance.business_type = validated_data.get('business_type', instance.business_type)
        instance.company_address = validated_data.get('company_address', instance.company_address)
        instance.company_postal_code = validated_data.get('company_postal_code', instance.company_postal_code)
        instance.company_description = validated_data.get('company_description', instance.company_description)
        instance.company_contact_person = validated_data.get('company_contact_person', instance.company_contact_person)
        instance.company_contact_detail = validated_data.get('company_contact_detail', instance.company_contact_detail)
        instance.credit_amount = validated_data.get('credit_amount', instance.credit_amount)
        instance.card_type = validated_data.get('card_type', instance.card_type)
        instance.card_number = validated_data.get('card_number', instance.card_number)
        instance.name_on_card = validated_data.get('name_on_card', instance.name_on_card)
        instance.expiration_date = validated_data.get('expiration_date', instance.expiration_date)
        instance.card_security_code = validated_data.get('card_security_code', instance.card_security_code)
        instance.billing_address = validated_data.get('billing_address', instance.billing_address)
        instance.city = validated_data.get('city', instance.city)
        instance.state_province = validated_data.get('state_province', instance.state_province)
        instance.zip_code = validated_data.get('zip_code', instance.zip_code)
        instance.billing_email = validated_data.get('billing_email', instance.billing_email)
        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.twitter = validated_data.get('twitter', instance.twitter)
        instance.instagram = validated_data.get('instagram', instance.instagram)

        instance.save()

        user.username = user_data.get('username', user.username)
        user.save()

        return instance


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    user = AccountSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ('user', 'nric_num', 'name_on_nric', 'nric_type', 'date_of_birth',
                  'preferred_name', 'photo', 'gender',
                  'contact_number', 'block_building', 'street_name', 'unit_number', 'postal_code',
                  'bank_number', 'branch_number', 'account_number',
                  'feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude', 'rating',
                  'referred_from',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
        read_only_fields = ('first_time_sign_in', 'last_edited_by',)


