from rest_framework import serializers

from . import models

ModelSerializer = serializers.ModelSerializer

class TicketTypeSerializer(ModelSerializer):
    class Meta:
        model = models.TicketType
        fields = (
            'id',
            'name',
            'event'
        )

class TicketTemplateSerializer(ModelSerializer):
    class Meta:
        model = models.TicketTemplate
        fields = (
            'id',
            'name',
            'event_type'
        )

class EntitledToRelatedField(serializers.RelatedField):
    def to_native(self, value):
        if isinstance(value, models.TicketType):
            typen = 'type'
            typev = TicketTypeSerializer(value)
        elif isinstance(value, models.TicketTemplate):
            typen = 'template'
            typev = TicketTemplateSerializer(value)
        else:
            raise Exception("Unexpected entitlement")

        return {'type': typen, 'value': typev.data}


class FlatEntitledToRelatedField(serializers.RelatedField):
    def to_native(self, value):
        if isinstance(value, models.TicketType):
            return {'type': 'type', 'pk': value.pk}
        elif isinstance(value, models.TicketTemplate):
            return {'type': 'template', 'pk': value.pk}
        raise Exception("Unexpected entitlement")

class EntitlementSerializer(ModelSerializer):
    entitled_to = EntitledToRelatedField()
    valid = serializers.Field(source='valid')

    class Meta:
        model = models.Entitlement
        fields = (
            'name',
            'entitled_to',
            'start_date', 'end_date',
            'valid'
        )

class PunterSerializer(ModelSerializer):
    entitlements = EntitlementSerializer(many=True)

    class Meta:
        model = models.Punter
        fields = (
            'id',
            'punter_type', 'name',
            'cid', 'login', 'swipecard', 'email',
            'comment',
            'entitlements',
            'tickets'
        )

class FlatPunterSerializer(ModelSerializer):
    entitlements = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = models.Punter
        fields = (
            'id',
            'punter_type', 'name',
            'cid', 'login', 'swipecard', 'email',
            'comment',
            'entitlements'
        )
