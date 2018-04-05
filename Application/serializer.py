from django.db.models import QuerySet
from rest_framework import serializers


def get_actual(obj):
    """Expands `obj` to the actual object type.
    """
    for name in dir(obj):
        try:
            attr = getattr(obj, name)
            if isinstance(attr, obj.__class__):
                return attr
        except:
            pass
    return obj


class ModelField(serializers.ChoiceField):
    """Defines field that names the model that underlies a serializer.
    """

    def __init__(self, *args, **kwargs):
        super(ModelField, self).__init__(*args, allow_null=True, **kwargs)

    def get_attribute(self, obj):
        return get_actual(obj)

    def to_representation(self, obj):
        return obj.__class__.__name__


class HyperlinkedModelHierarchySerializer(serializers.HyperlinkedModelSerializer):
    """Extends the `HyperlinkedModelSerializer` to properly handle class hierearchies.

    For an hypothetical model `BaseModel`, serializers from this
    class are capable of also handling those models that are derived
    from `BaseModel`.

    The `Meta` class must whitelist the derived `models` to be
    allowed. It also must declare the `model_dependent_fields`
    attribute and those fields must also be added to its `fields`
    attribute, for example:

        wing = serializers.CharField(allow_null=True)
        tail = serializers.CharField(allow_null=True)

        class Meta:
            model = Animal
            models = (Bird, Dog)
            model_dependent_fields = ('wing', 'tail')
            fields = ('model', 'id', 'name') + model_dependent_fields
            read_only_fields = ('id',)

    The `model` field is defined by this class.
    """
    model = ModelField(choices=[])

    def __init__(self, *args, **kwargs):
        """Instantiates and filters fields.

        Keeps all fields if this serializer is processing a CREATE
        request. Retains only those fields that are independent of
        the particular model implementation otherwise.
        """
        super(HyperlinkedModelHierarchySerializer, self).__init__(*args, **kwargs)
        # complete the meta data
        self.Meta.models_by_name = {model.__name__: model for model in self.Meta.models}
        self.Meta.model_names = self.Meta.models_by_name.keys()
        # update valid model choices,
        # mark the model as writable if this is a CREATE request
        self.fields['model'] = ModelField(choices=self.Meta.model_names, read_only=bool(self.instance))

        def remove_missing_fields(obj):
            # drop those fields model-dependent fields that `obj` misses
            unused_field_keys = set()
            for field_key in self.Meta.model_dependent_fields:
                if not hasattr(obj, field_key):
                    unused_field_keys |= {field_key}
            for unused_field_key in unused_field_keys:
                self.fields.pop(unused_field_key)

        if not self.instance is None:
            # processing an UPDATE, LIST, RETRIEVE or DELETE request
            if not isinstance(self.instance, QuerySet):
                # this is an UPDATE, RETRIEVE or DELETE request,
                # retain only those fields that are present on the processed instance
                self.instance = get_actual(self.instance)
                remove_missing_fields(self.instance)
            else:
                # this is a LIST request, retain only those fields
                # that are independent of the particular model implementation
                for field_key in self.Meta.model_dependent_fields:
                    self.fields.pop(field_key)

    def validate_model(self, value):
        """Validates the `model` field.
        """
        if self.instance is None:
            # validate for CREATE
            if value not in self.Meta.model_names:
                raise serializers.ValidationError('Must be one of: ' + (', '.join(self.Meta.model_names)))
            else:
                return value
        else:
            # model cannot be changed
            return get_actual(self.instance).__class__.__name__

    def create(self, validated_data):
        """Creates instance w.r.t. the value of the `model` field.
        """
        model = self.Meta.models_by_name[validated_data.pop('model')]
        for field_key in self.Meta.model_dependent_fields:
            if not field_key in model._meta.get_all_field_names():
                validated_data.pop(field_key)
                self.fields.pop(field_key)
        return model.objects.create(**validated_data)