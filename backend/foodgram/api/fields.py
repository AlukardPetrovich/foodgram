import base64
import uuid

from django.core.files.base import ContentFile
from rest_framework.serializers import Field


class CustomImageField(Field):

    def to_internal_value(self, data):
        header, file_data = data.split(';base64,')
        decoded_file = base64.b64decode(file_data)
        _, file_extension = header.split('/')
        file_name = uuid.uuid4()
        full_file_name = str(file_name) + '.' + file_extension
        return ContentFile(decoded_file, name=full_file_name)

    def to_representation(self, value):
        return str(value)
