from Application.settings import INSTANCE_TYPE
from Sensors.models import MotionSensor, Sensor
import _thread


def setup():
    if INSTANCE_TYPE == 'CLIENT':
        setup_motion()


def setup_motion():
    import RPi.GPIO as GPIO
    classes = Sensor.__subclasses__()
    for cls in classes:
        sensors = cls.objects.all()
        GPIO.setmode(GPIO.BOARD)
        for sensor in sensors:
            _thread.start_new_thread(sensor.run,(sensor,))
