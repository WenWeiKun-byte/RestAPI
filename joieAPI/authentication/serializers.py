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
        fields = ('url', 'user', 'company_name', 'roc_number', 'business_type', 'ea_number', 'company_address',
                  'company_postal_code', 'company_description', 'company_contact_person',
                  'company_contact_detail', 'company_logo',
                  'credit_amount', 'card_type', 'card_number', 'name_on_card', 'expiration_date',
                  'card_security_code', 'billing_address', 'city', 'state_province', 'zip_code', 'billing_email',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
        read_only_fields = ('first_time_sign_in', 'last_edited_by',)    # not expose to endpoint but can update at view

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

        instance.status = validated_data.get('status', instance.status)
        instance.first_time_sign_in = validated_data.get('first_time_sign_in', instance.first_time_sign_in)
        instance.last_edited_by = validated_data.get('last_edited_by', instance.last_edited_by)

        instance.save()

        user.username = user_data.get('username', user.username)
        user.save()

        return instance


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    user = AccountSerializer()

    class Meta:
        model = EmployeeProfile
        fields = ('url', 'user', 'nric_num', 'name_on_nric', 'nric_type', 'date_of_birth',
                  'preferred_name', 'photo', 'gender',
                  'contact_number', 'block_building', 'street_name', 'unit_number', 'postal_code',
                  'bank_number', 'branch_number', 'account_number',
                  'feedback_score_punctuality', 'feedback_score_job_performance', 'feedback_score_attitude', 'rating',
                  'referred_from',
                  'facebook', 'twitter', 'instagram',
                  'status', 'first_time_sign_in', 'last_edited_by')
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
        instance.bank_number = validated_data.get('bank_number', instance.bank_number)
        instance.branch_number = validated_data.get('branch_number', instance.branch_number)
        instance.account_number = validated_data.get('account_number', instance.account_number)

        instance.feedback_score_punctuality = validated_data.get('feedback_score_punctuality', instance.feedback_score_punctuality)
        instance.feedback_score_job_performance = validated_data.get('feedback_score_job_performance', instance.feedback_score_job_performance)
        instance.feedback_score_attitude = validated_data.get('feedback_score_attitude', instance.feedback_score_attitude)
        instance.rating = validated_data.get('rating', instance.rating)
        instance.referred_from = validated_data.get('referred_from', instance.referred_from)

        instance.facebook = validated_data.get('facebook', instance.facebook)
        instance.twitter = validated_data.get('twitter', instance.twitter)
        instance.instagram = validated_data.get('instagram', instance.instagram)

        instance.status = validated_data.get('status', instance.status)
        instance.first_time_sign_in = validated_data.get('first_time_sign_in', instance.first_time_sign_in)
        instance.last_edited_by = validated_data.get('last_edited_by', instance.last_edited_by)

        instance.save()

        user.username = user_data.get('username', user.username)
        user.save()

        return instance


