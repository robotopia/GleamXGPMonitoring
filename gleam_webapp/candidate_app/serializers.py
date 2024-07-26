from rest_framework import serializers
from . import models


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Observation
        fields = "__all__"


class MetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Metadata
        fields = "__all__"


class CandidateSerializer(serializers.ModelSerializer):
    metadata = serializers.CharField(source="metadata.text")
    project = serializers.CharField(source="project.name")

    class Meta:
        model = models.Candidate
        fields = "__all__"

    # When calling this serializer we actually create two objects
    # A candidate and optionally a metadata
    def create(self, validated_data):
        metadata_data = validated_data.pop("metadata", None)
        project_name = validated_data.pop("project")["name"]
        project = models.Project.objects.get(name=project_name)
        candidate = models.Candidate.objects.create(project=project, **validated_data)
        if metadata_data:
            models.Metadata.objects.create(candidate=candidate, **metadata_data)
        return candidate

    def update(self, instance, validated_data):
        metadata_data = validated_data.pop("metadata", None)
        project_name = validated_data.pop("project")["name"]
        project = models.Project.objects.get(name=project_name)
        instance.project = project
        instance.save()

        if metadata_data:
            # Update or create the Metadata object
            if hasattr(instance, "metadata"):
                isinstance.metadata.text = metadata_data
                instance.metadata.save()
            else:
                models.Metadata.objects.create(candidate=instance, **metadata_data)
        return instance
