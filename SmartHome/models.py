from django.db import models

# Create your models here.
from django.db.models import signals

from Actors.models import Actor, Configuration
from Sensors.models import Sensor



class Peer(models.Model):
    address = models.GenericIPAddressField()
    name = models.CharField(max_length=20)
    server = models.GenericIPAddressField()

    def __str__(self):
        return self.address

    def __unicode__(self):
        return self.address


class Condition(models.Model):
    # if given this is an AND, if not this is an OR
    pre_condition = models.ForeignKey('Condition', null=True, blank=True, related_name='post_condition')
    sensor = models.ForeignKey(Sensor)
    # the value to check
    trigger_value = models.CharField(max_length=100)
    # such as gt, eq, lt, ...
    condition = models.CharField(max_length=5)


class Action(models.Model):
    actor = models.ForeignKey(Actor)
    configuration = models.ForeignKey(Configuration)


class Event(models.Model):
    conditions = models.ManyToManyField(Condition)
    actions = models.ManyToManyField(Action)
    duration = models.IntegerField()
    action = models.CharField(max_length=100)

    @staticmethod
    def _post_hook(sender, instance, created, **kwargs):
        if created:
            from SmartHome.controller import controller
            controller.create_event_scheduler(instance)


signals.post_save.connect(Event._post_hook, sender=Event)
