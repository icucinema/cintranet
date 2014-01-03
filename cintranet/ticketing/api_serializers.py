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
            raise Exception("Unexpected entitlement - %s" % (str(type(value)),))

        return {'type': typen, 'value': typev.data}


class FlatEntitledToRelatedField(serializers.RelatedField):
    def to_native(self, value):
        if isinstance(value, models.TicketType):
            return {'type': 'type', 'pk': value.pk}
        elif isinstance(value, models.TicketTemplate):
            return {'type': 'template', 'pk': value.pk}
        raise Exception("Unexpected entitlement")

class EntitlementSerializer(ModelSerializer):
    entitled_to = EntitledToRelatedField(source='entitled_to_subclasses', many=True)
    valid = serializers.Field(source='valid')

    class Meta:
        model = models.Entitlement
        fields = (
            'id',
            'name',
            'entitled_to',
            'start_date', 'end_date',
            'valid'
        )

class TicketSerializer(ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = (
            'id', 'punter', 'entitlement', 'timestamp', 'status', 'ticket_type'
        )

class EntitlementDetailSerializer(ModelSerializer):
    entitlement = EntitlementSerializer()
    valid = serializers.Field(source='valid')

    class Meta:
        model = models.EntitlementDetail
        fields = (
            'id',
            'remaining_uses',
            'entitlement', 'valid'
        )

class PunterSerializer(ModelSerializer):
    entitlement_details = EntitlementDetailSerializer(many=True)

    class Meta:
        model = models.Punter
        fields = (
            'id',
            'punter_type', 'name',
            'cid', 'login', 'swipecard', 'email',
            'comment',
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

class FilmSerializer(ModelSerializer):
    class Meta:
        model = models.Film
        fields = (
            'id', 'name', 'description', 'tmdb_id', 'imdb_id', 'poster_url'
        )
