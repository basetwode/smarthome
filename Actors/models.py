import json
from abc import abstractmethod

from django.db import models
from django.db.models import signals
from model_utils.managers import InheritanceManager
from requests_futures.sessions import FuturesSession


from Actors.validators import validate_rgb, validate_brightness
from Application.settings import INSTANCE_TYPE
from Application.utils import create_request_context


class Configuration(models.Model):
    name = models.CharField(max_length=20)

    @staticmethod
    @abstractmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        # If this configuration is active in an associated actor, a reload is triggered.

        for actor in instance.active_config.all():
            for cls in Actor.__subclasses__():
                cls_name = cls.__name__.lower()
                if hasattr(actor, cls_name):
                    actor = getattr(actor, cls_name)
                    actor._post_hook_peer(sender, actor, False, **kwargs)


    @staticmethod
    @abstractmethod
    def _post_hook_server(sender, instance, created, **kwargs):

        put_url = 'http://{url}/configuration/{type}/{id}/'
        post_url = 'http://{url}/configuration/{type}/'
        from SmartHome.models import Peer
        for peer in Peer.objects.all():
            from Actors import serializers
            requests = FuturesSession(max_workers=10)
            url = str.format(post_url if created else put_url, url=peer.address,
                             type=instance.__class__.__name__.lower(),
                             id=instance.id)
            context = create_request_context()

            Serializer = getattr(serializers, instance.__class__.__name__ + 'Serializer')

            serializer_instance = Serializer(instance, context=context)
            if created:
                response = requests.post(url, json.dumps(serializer_instance.data),
                                         headers={'Content-Type': 'application/json'})
            else:
                response = requests.put(url, json.dumps(serializer_instance.data),
                                        headers={'Content-Type': 'application/json'})

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class LEDConfiguration(Configuration):
    red = models.IntegerField(validators=[validate_rgb])
    green = models.IntegerField(validators=[validate_rgb])
    blue = models.IntegerField(validators=[validate_rgb])
    brightness = models.IntegerField(validators=[validate_brightness])
    frequency = models.IntegerField()

    @staticmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        super(LEDConfiguration, LEDConfiguration)._post_hook_peer(sender, instance, created, **kwargs)

    @staticmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        super(LEDConfiguration, LEDConfiguration)._post_hook_server(sender, instance, created, **kwargs)


class Actor(models.Model):
    name = models.CharField(max_length=10)
    peer = models.ForeignKey('SmartHome.Peer')
    active_config = models.ForeignKey(Configuration, related_name='active_config')
    on_config = models.ForeignKey(Configuration, related_name='on_config')
    off_config = models.ForeignKey(Configuration, related_name='off_config')
    objects = InheritanceManager()

    @staticmethod
    @abstractmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        print('post hook peer')

    @staticmethod
    @abstractmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        print('post hook server')
        from Actors import serializers
        requests = FuturesSession(max_workers=10)
        put_url = 'http://{url}/{type}/{name}/{id}/'
        post_url = 'http://{url}/{type}/{name}/'
        url = str.format(post_url if created else put_url, url=instance.peer.address, type='actors',
                         name=instance.__class__.__name__.lower(),
                         id=instance.id)
        context = create_request_context()

        Serializer = getattr(serializers, instance.__class__.__name__ + 'Serializer')

        serializer_instance = Serializer(instance, context=context)
        if created:
            response = requests.post(url, json.dumps(serializer_instance.data),
                                     headers={'Content-Type': 'application/json'})
        else:
            response = requests.put(url, json.dumps(serializer_instance.data),
                                    headers={'Content-Type': 'application/json'})

    def __unicode__(self):
        return self.name


class LEDActor(Actor):
    red_channel = models.IntegerField()
    green_channel = models.IntegerField()
    blue_channel = models.IntegerField()

    @staticmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        print("post hook")
        from Actors.setup import led_pwm
        active_config = instance.active_config.ledconfiguration
        led_pwm.set_pwm(instance.red_channel, 0,
                        LEDActor.calc_pwm_val(active_config.red, active_config.brightness))
        led_pwm.set_pwm(instance.green_channel, 0,
                        LEDActor.calc_pwm_val(active_config.green, active_config.brightness))
        led_pwm.set_pwm(instance.blue_channel, 0,
                        LEDActor.calc_pwm_val(active_config.blue, active_config.brightness))
        led_pwm.set_pwm_freq(active_config.frequency)

    @staticmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        super(LEDActor, LEDActor)._post_hook_server(sender, instance, created, **kwargs)

    @staticmethod
    def calc_pwm_val(value, brightness):
        return int((float(value) / 255) * (float(brightness) / 100) * 4095)


for cls in Actor.__subclasses__():
    signals.post_save.connect(cls._post_hook_peer if INSTANCE_TYPE == 'CLIENT' else cls._post_hook_server, sender=cls)
for cls in Configuration.__subclasses__():
    signals.post_save.connect(cls._post_hook_peer if INSTANCE_TYPE == 'CLIENT' else cls._post_hook_server, sender=cls)
