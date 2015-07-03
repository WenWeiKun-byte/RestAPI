from rest_framework import serializers


AVAILABLE_ACTIONS = {'JOB_PUBLISH': 'publish',
                     }


class ModelChoiceField(serializers.ChoiceField):
    """
    new serializers field for model choice
    """
    def to_representation(self, value):
        if value in ('', None):
            return value
        return value.get_name()


class ImageField(serializers.ImageField):

    def to_internal_value(self, data):
                # if data is None image field was not uploaded
        if data:
            file_object = super(ImageField, self).to_internal_value(data)
            django_field = self._DjangoImageField()
            django_field.error_messages = self.error_messages
            django_field.to_python(file_object)
            return file_object
        return data


class ActionSerializer(serializers.Serializer):
    action = serializers.CharField()