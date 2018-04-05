from django.contrib import admin

# Register your models here.
from Sensors.models import MotionSensor, SensorData, LightSensor

admin.site.register(MotionSensor)
admin.site.register(SensorData)
admin.site.register(LightSensor)
