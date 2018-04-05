from django.db.models import QuerySet
from rest_framework import serializers, viewsets, routers

from Actors.models import LEDActor, Actor
from Application.serializer import HyperlinkedModelHierarchySerializer
from Sensors.models import Sensor
from SmartHome.models import Condition, Peer, Action, Event


class ActorSerializer(HyperlinkedModelHierarchySerializer):
    class Meta:
        model = Actor
        models = Actor.__subclasses__()
        fields = '__all__'
        model_dependent_fields = ()


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class SensorSerializer(HyperlinkedModelHierarchySerializer):
    class Meta:
        model = Sensor
        models = Sensor.__subclasses__()
        fields = '__all__'
        model_dependent_fields = ()


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer


class ConditionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Condition
        fields = '__all__'


class ConditionViewSet(viewsets.ModelViewSet):
    queryset = Condition.objects.all()
    serializer_class = ConditionSerializer


class PeerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Peer
        fields = '__all__'


class PeerViewSet(viewsets.ModelViewSet):
    queryset = Peer.objects.all()
    serializer_class = PeerSerializer


class ActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'


class ActionViewSet(viewsets.ModelViewSet):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer


class EventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
