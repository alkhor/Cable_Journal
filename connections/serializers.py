from rest_framework import serializers
from connections.models import DiscoverData

class DiscoverDataSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    ip = serializers.models.TextField()
    mac = serializers.models.TextField()
    switch = serializers.models.TextField()
    port = serializers.models.TextField()
    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return DiscoverData.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `Snippet` instance, given the validated data.
        """
        instance.title = validated_data.get('ip', instance.ip)
        instance.code = validated_data.get('mac', instance.mac)
        instance.linenos = validated_data.get('switch', instance.switc)
        instance.language = validated_data.get('port', instance.port)
        instance.save()
        return instance
