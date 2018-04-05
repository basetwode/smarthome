import json
import traceback
import time
from abc import abstractmethod
from django.db import models
from requests_futures.sessions import FuturesSession

from Application.settings import INSTANCE_TYPE
# Create your models here.
from django.db.models import signals

from Application.utils import create_request_context


class Sensor(models.Model):
    name = models.CharField(max_length=10)
    peer = models.ForeignKey('SmartHome.Peer')

    @staticmethod
    @abstractmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        if created and INSTANCE_TYPE == 'CLIENT':
            import _thread
            _thread.start_new_thread(instance.run, (instance,))
            print("new sensor created. started new thread")
            # on client this should trigger a post to server

    @staticmethod
    @abstractmethod
    def _post_hook_server(sender, instance, created, **kwargs):

        from Sensors import serializers

        requests = FuturesSession(max_workers=10)
        put_url = 'http://{url}/{type}/{name}/{id}/'
        post_url = 'http://{url}/{type}/{name}/'
        url = str.format(post_url if created else put_url, url=instance.peer.address, type='sensors',
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

    @staticmethod
    @abstractmethod
    def run(sensor_instance, running=True):
        pass


class LightSensor(Sensor):
    # light = models.IntegerField()
    light_threshold = models.IntegerField()
    pin = models.IntegerField()

    @staticmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        super(LightSensor, LightSensor)._post_hook_peer(sender, instance, created, **kwargs)

    @staticmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        super(LightSensor, LightSensor)._post_hook_server(sender, instance, created, **kwargs)

    @staticmethod
    def run(sensor_instance, running=True):
        try:
            import RPi.GPIO as GPIO
            GPIO.setup(sensor_instance.pin, GPIO.IN)
            while running:

                previous_data = SensorData.objects.filter(sensor=sensor_instance).order_by('date')[:1]

                count = 0
                GPIO.setup(sensor_instance.pin, GPIO.OUT)
                GPIO.output(sensor_instance.pin, GPIO.LOW)
                time.sleep(0.5)

                # Change the pin back to input
                GPIO.setup(sensor_instance.pin, GPIO.IN)
                while GPIO.input(sensor_instance.pin) == GPIO.LOW:
                    count += 1
                light_now = SensorData(sensor=sensor_instance, value=count)
                light_before = SensorData(value=0)

                if len(previous_data) > 0:
                    light_before = previous_data[0]

                if abs(int(light_before.value) - int(light_now.value)) > sensor_instance.light_threshold:
                    print(light_before.value, light_now.value)
                    light_now.save()
                time.sleep(5)

        except Exception as e:
            print(e)
            tb = traceback.format_exc()
            print(tb)
            print("Error occurred")
            pass
        finally:
            running = False
            GPIO.cleanup()

    def __str__(self):
        return "Light %s" % self.pin

    def __unicode__(self):
        return "Light %s" % self.pin


class MotionSensor(Sensor):

    pin = models.IntegerField()

    @staticmethod
    def _post_hook_peer(sender, instance, created, **kwargs):
        super(MotionSensor, MotionSensor)._post_hook_peer(sender, instance, created, **kwargs)

    @staticmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        super(MotionSensor, MotionSensor)._post_hook_server(sender, instance, created, **kwargs)

    @staticmethod
    def run(sensor_instance, running=True):
        try:
            import RPi.GPIO as GPIO
            GPIO.setup(sensor_instance.pin, GPIO.IN)
            while running:
                previous_data = SensorData.objects.filter(sensor=sensor_instance).order_by('-date')[:1]
                motion_detected_now = SensorData(sensor=sensor_instance, value=GPIO.input(sensor_instance.pin))

                motion_detected_before = SensorData(value=0)
                if len(previous_data) > 0:
                    motion_detected_before = previous_data[0]

                if int(motion_detected_now.value) != int(motion_detected_before.value):
                    motion_detected_now.save()

                time.sleep(0.1)
        except Exception as e:
            print(e)
            tb = traceback.format_exc()
            print(tb)
            print("Error occurred")
            pass
        finally:
            running = False
            GPIO.cleanup()

    def __str__(self):
        return "Motion %s" % self.pin

    def __unicode__(self):
        return "Motion %s" % self.pin


class SensorData(models.Model):
    value = models.CharField(max_length=40)
    sensor = models.ForeignKey(Sensor)
    date = models.DateTimeField(auto_now=True)

    @staticmethod
    def _post_hook_peer(sender, instance, created, **kwargs):

        requests = FuturesSession(max_workers=10)
        from Sensors import serializers

        post_url = 'http://{url}/{type}/'
        url = str.format(post_url, url=instance.sensor.peer.server, type='data',
                         id=instance.id)
        context = create_request_context()
        Serializer = getattr(serializers, instance.__class__.__name__ + 'Serializer')
        serializer_instance = Serializer(instance, context=context)
        print(json.dumps(serializer_instance.data))
        response = requests.post(url, json.dumps(serializer_instance.data),
                                 headers={'Content-Type': 'application/json'})
        sensor_data = SensorData.objects.filter(sensor=instance.sensor).order_by('-date')
        if len(sensor_data) > 10:
            for sensor_data_item in sensor_data[10:]:
                sensor_data_item.delete()

    @staticmethod
    def _post_hook_server(sender, instance, created, **kwargs):
        print("data received: ", instance.value, instance.sensor.name)
        sensor_data = SensorData.objects.filter(sensor=instance.sensor).order_by('-date')
        from SmartHome.controller import controller
        controller.put_data(instance)
        if len(sensor_data) > 10:
            for sensor_data_item in sensor_data[10:]:
                sensor_data_item.delete()


signals.post_save.connect(SensorData._post_hook_peer if INSTANCE_TYPE == 'CLIENT' else SensorData._post_hook_server,
                          sender=SensorData)
for cls in Sensor.__subclasses__():
    signals.post_save.connect(cls._post_hook_peer if INSTANCE_TYPE == 'CLIENT' else cls._post_hook_server, sender=cls)
