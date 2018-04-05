from rest_framework import routers

from Actors.serializers import LedActorViewSet, LEDConfigurationViewSet, ConfigurationViewSet
from Application.settings import INSTANCE_TYPE
from Sensors.serializers import MotionSensorViewSet, LightSensorViewSet, SensorDataViewSet
from SmartHome.serializers import PeerViewSet, ConditionViewSet, ActionViewSet, EventViewSet, SensorViewSet, \
    ActorViewSet

router = routers.DefaultRouter()

router.register(r'actors/ledactor', LedActorViewSet)
router.register(r'sensors/motionsensor', MotionSensorViewSet)
router.register(r'sensors/lightsensor', LightSensorViewSet)
router.register(r'smart/peer', PeerViewSet)
router.register(r'data', SensorDataViewSet)
router.register(r'sensors', SensorViewSet)
router.register(r'actors', ActorViewSet)
router.register(r'configuration/ledconfiguration', LEDConfigurationViewSet)
router.register(r'configuration', ConfigurationViewSet)

if INSTANCE_TYPE == 'SERVER':
    router.register(r'smart/condition', ConditionViewSet)
    router.register(r'smart/action', ActionViewSet)
    router.register(r'smart/event', EventViewSet)
