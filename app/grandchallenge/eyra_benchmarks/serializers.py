from guardian.shortcuts import get_perms
from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from grandchallenge.eyra_benchmarks.models import Benchmark, Submission


class Permissions(serializers.Field):
    def to_representation(self, instance):
        user = self.context['request'].user
        return get_perms(user, instance)

    class Meta:
        swagger_schema_fields = {
            'type': 'array',
            'items': {'type': 'integer'}
        }


class BenchmarkSerializer(serializers.ModelSerializer):
    creator = PrimaryKeyRelatedField(read_only=True)
    permissions = Permissions(read_only=True)

    class Meta:
        model = Benchmark
        fields = [*[f.name for f in Benchmark._meta.fields], 'permissions']


class SubmissionSerializer(serializers.ModelSerializer):
    creator = PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Submission
        fields = '__all__'
