from rest_framework import serializers

from . import models

ModelSerializer = serializers.HyperlinkedModelSerializer

class DistributorSerializer(ModelSerializer):
    class Meta:
        model = models.Distributor
        fields = (
            'url', 'id', 'name', 'via_troy', 'royalties_percent', 'royalties_minimum'
        )

class TicketTypeSerializer(ModelSerializer):
    class Meta:
        model = models.TicketType
        fields = (
            'url', 'id',
            'name',
            'event',
            'template',
            'box_office_return_price', 'sale_price',
            'is_public',
            'sell_online', 'sell_on_the_door',
            'general_availability',
        )

class TicketTemplateSerializer(ModelSerializer):
    class Meta:
        model = models.TicketTemplate
        fields = (
            'url', 'id',
            'name',
            'event_type',
            'box_office_return_price', 'sale_price',
            'is_public',
            'sell_online', 'sell_on_the_door',
            'general_availability',
        )

class EventTypeSerializer(ModelSerializer):
    ticket_templates = TicketTemplateSerializer(many=True)

    class Meta:
        model = models.EventType
        fields = (
            'url', 'id',
            'name', 'ticket_templates'
        )

class EntitledToRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        kwargs = {'context': self.context}
        if isinstance(value, models.TicketType):
            typen = 'type'
            typev = TicketTypeSerializer(value, **kwargs)
        elif isinstance(value, models.TicketTemplate):
            typen = 'template'
            typev = TicketTemplateSerializer(value, **kwargs)
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
    entitled_to = EntitledToRelatedField(source='entitled_to_subclasses', many=True, read_only=True)
    valid = serializers.ReadOnlyField()

    class Meta:
        model = models.Entitlement
        fields = (
            'url', 'id',
            'name',
            'entitled_to',
            'start_date', 'end_date',
            'valid'
        )

class TicketSerializer(ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = (
            'url', 'id', 'punter', 'entitlement', 'timestamp', 'status', 'ticket_type'
        )

class EntitlementDetailSerializer(ModelSerializer):
    entitlement = EntitlementSerializer(read_only=True)
    valid = serializers.ReadOnlyField()

    class Meta:
        model = models.EntitlementDetail
        fields = (
            'url', 'id',
            'remaining_uses',
            'entitlement', 'valid'
        )

class PunterIdentifierSerializer(ModelSerializer):
    class Meta:
        model = models.PunterIdentifier
        fields = (
            'url', 'id',
            'type', 'value'
        )

class PunterSerializer(ModelSerializer):
    entitlement_details = EntitlementDetailSerializer(many=True, read_only=True)
    identifiers = PunterIdentifierSerializer(many=True, read_only=True)

    class Meta:
        model = models.Punter
        fields = (
            'url', 'id',
            'punter_type', 'name',
            'cid', 'login', 'email',
            'comment', 'identifiers',
            'entitlement_details',
        )

class FilmSerializer(ModelSerializer):
    distributor = DistributorSerializer()
    images = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(FilmSerializer, self).__init__(*args, **kwargs)

        self.with_images = False
        self.with_videos = False
        if 'request' in self.context and self.context['request'].query_params.get('with_images'):
            self.with_images = True
        if 'request' in self.context and self.context['request'].query_params.get('with_videos'):
            self.with_videos = True

    def get_images(self, obj):
        if not self.with_images:
            return {}

        images = getattr(obj, '_images', None)
        if images:
            return images
        return obj.fetch_tmdb_images()

    def get_videos(self, obj):
        if not self.with_videos:
            return {}

        videos = getattr(obj, '_videos', None)
        if videos:
            return videos
        return obj.fetch_tmdb_videos()

    class Meta:
        model = models.Film
        fields = (
            'url', 'id', 'name', 'description', 'short_description', 'tmdb_id', 'imdb_id', 'rotten_tomatoes_id', 'poster_url', 'hero_image_url', 'certificate',
            'is_public', 'distributor', 'images', 'videos', 'youtube_id', 'length'
        )

class FlatFilmSerializer(ModelSerializer):
    class Meta:
        model = models.Film
        fields = (
            'url', 'id', 'name', 'description', 'short_description', 'tmdb_id', 'imdb_id', 'rotten_tomatoes_id', 'poster_url', 'hero_image_url', 'certificate',
            'is_public', 'distributor', 'youtube_id', 'length'
        )

class ShowingSerializer(ModelSerializer):
    primary_event = serializers.HyperlinkedRelatedField(read_only=True, required=False, view_name='event-detail')
    film_title = serializers.SlugRelatedField(read_only=True, slug_field='name', source='film')
    film = FilmSerializer(source='week.film')

    class Meta:
        model = models.Showing
        fields = (
            'url', 'id', 'film', 'primary_event', 'start_time', 'film_title', 'is_public', 'banner_text'
        )

class FlatShowingSerializer(ModelSerializer):
    primary_event = serializers.HyperlinkedRelatedField(read_only=True, required=False, view_name='event-detail')
    film = serializers.HyperlinkedRelatedField(required=True, view_name='film-detail', queryset=models.Film.objects.all())

    class Meta:
        model = models.Showing
        fields = (
            'url', 'id', 'film', 'primary_event', 'start_time', 'is_public', 'banner_text'
        )

class BoxOfficeReturnSerializer(ModelSerializer):
    fake_filename = serializers.CharField()

    class Meta:
        model = models.BoxOfficeReturn
        fields = (
            'id', 'film', 'start_time', 'pdf_file', 'fake_filename'
        )

class GroupedShowing(object):
    def __init__(self, start_time, showings):
        self.start_time = start_time
        self.showings = showings

        self.box_office_return = None
        if len(self.showings) > 0:
            self.box_office_return = self.showings[0].film.box_office_returns.filter(start_time=start_time).first()

class GroupedShowingSerializer(serializers.Serializer):
    start_time = serializers.DateField()
    showings = ShowingSerializer(many=True)
    box_office_return = BoxOfficeReturnSerializer()

    def __init__(self, instance, *args, **kwargs):
        from bor_generator import get_show_week
        # right, process it!
        datasets = {}
        for obj in instance:
            datasets.setdefault(get_show_week(obj.start_time), []).append(obj)
        
        munged_dataset = sorted((GroupedShowing(start_time, objs) for start_time, objs in datasets.iteritems()), key=lambda z: z.start_time)

        super(GroupedShowingSerializer, self).__init__(munged_dataset, *args, **kwargs)

class ShowingsWeekSerializer(ModelSerializer):
    start_time = serializers.DateTimeField(format='%Y-%m-%d')
    showings = ShowingSerializer(many=True)
    box_office_return = BoxOfficeReturnSerializer()

    class Meta:
        model = models.ShowingsWeek
        fields = (
            'url', 'id', 'start_time', 'showings', 'box_office_return',
            'film', 'royalties_percent', 'royalties_minimum', 'royalties_troytastic'
        )

class EventSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = (
            'url', 'id', 'name', 'showings', 'event_types', 'start_time'
        )

class ComprehensiveTicketTypeSerializer(ModelSerializer):
    event = EventSerializer(read_only=True)
    class Meta:
        model = models.TicketType
        fields = (
            'url', 'id',
            'name',
            'event',
            'box_office_return_price', 'sale_price'
        )

class ComprehensiveTicketSerializer(ModelSerializer):
    entitlement = EntitlementSerializer(read_only=True)
    ticket_type = ComprehensiveTicketTypeSerializer(read_only=True)
    punter = PunterSerializer(read_only=True)

    class Meta:
        model = models.Ticket
        fields = (
            'url', 'id', 'punter', 'entitlement', 'timestamp', 'status', 'ticket_type'
        )

