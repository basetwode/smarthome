from rest_framework import serializers, viewsets, routers

from Sensors.models import MotionSensor, LightSensor, SensorData


class MotionSensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = MotionSensor
        fields = '__all__'


class MotionSensorViewSet(viewsets.ModelViewSet):
    queryset = MotionSensor.objects.all()
    serializer_class = MotionSensorSerializer


class LightSensorSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = LightSensor
        fields = '__all__'


class LightSensorViewSet(viewsets.ModelViewSet):
    queryset = LightSensor.objects.all()
    serializer_class = LightSensorSerializer


class SensorDataSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = SensorData
        fields = '__all__'


class SensorDataViewSet(viewsets.ModelViewSet):
    queryset = SensorData.objects.all()
    serializer_class = SensorDataSerializer
