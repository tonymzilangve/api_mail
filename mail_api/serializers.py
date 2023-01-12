from rest_framework import serializers
from .models import *


class MailSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Mail()._meta.get_field('id'))

    class Meta:
        model = Mail
        fields = ('id', 'start_at', 'stop_at', 'text', 'clients', 'status', 'schedule')


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'mobile', 'operator', 'timezone', 'tag', 'tag_list')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('id', 'receiver', 'mail', 'sent_at', 'sent_status')

