from rest_framework import serializers, viewsets, mixins


AVAILABLE_ACTIONS = {'JOB_PUBLISH': 'publish',
                     'JOB_COPY': 'copy',
                     'JOB_APPLY': 'apply',
                     'JOB_APPROVE': 'approve',
                     'JOB_REJECT': 'reject',
                     }


class ModelChoiceField(serializers.ChoiceField):
    """
    new serializers.py field for model choice
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


class ReadDestroyViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """
    A viewset that provides default `list()`, 'destroy()' and `retrieve()` actions.
    use for actived job management
    """
    pass