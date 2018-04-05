from rest_framework import serializers, viewsets, routers

from Actors.models import LEDActor, LEDConfiguration, Configuration
from Application.serializer import HyperlinkedModelHierarchySerializer


class LEDActorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = LEDActor
        fields = '__all__'


class LedActorViewSet(viewsets.ModelViewSet):
    queryset = LEDActor.objects.all()
    serializer_class = LEDActorSerializer


class LEDConfigurationSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = LEDConfiguration
        fields = '__all__'


class LEDConfigurationViewSet(viewsets.ModelViewSet):
    queryset = LEDConfiguration.objects.all()
    serializer_class = LEDConfigurationSerializer


class ConfigurationSerializer(HyperlinkedModelHierarchySerializer):
    class Meta:
        model = Configuration
        models = Configuration.__subclasses__()
        fields = '__all__'
        model_dependent_fields = ()


class ConfigurationViewSet(viewsets.ModelViewSet):
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
