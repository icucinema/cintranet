from rest_framework import viewsets, filters
from rest_framework.decorators import action, link
from rest_framework.response import Response

from . import models, api_serializers

def top_level_action(methods=['post'], **kwargs):
    def decorator(func):
        func.toplevel_bind_to_methods = methods
        func.kwargs = kwargs
        return func
    return decorator

def serialize_queryset(self, serializer_class, queryset):
    self.serializer_class = serializer_class#api_serializers.EntitlementDetailSerializer
    self.paginate_by = None
    self.object_list = queryset

    page = self.paginate_queryset(self.object_list)
    if page is not None:
        serializer = self.get_pagination_serializer(page)
    else:
        serializer = self.get_serializer(self.object_list, many=True)

    return Response(serializer.data)

class TicketTemplateViewSet(viewsets.ModelViewSet):
    queryset = models.TicketTemplate.objects.all()
    serializer_class = api_serializers.TicketTemplateSerializer

class TicketTypeViewSet(viewsets.ModelViewSet):
    queryset = models.TicketType.objects.all()
    serializer_class = api_serializers.TicketTypeSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = models.Ticket.objects.all()
    serializer_class = api_serializers.TicketSerializer

class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = models.EventType.objects.all()
    serializer_class = api_serializers.EventTypeSerializer

class PunterViewSet(viewsets.ModelViewSet):
    queryset = models.Punter.objects.all()
    serializer_class = api_serializers.PunterSerializer
    filter_fields = ('punter_type',)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'cid', 'login', 'email')

    def list(self, request, *args, **kwargs):
        return super(PunterViewSet, self).list(request, *args, **kwargs)

    @action(methods=['GET'])
    def entitlement_details(self, request, pk=None):
        punter = self.get_object()
        return serialize_queryset(self, api_serializers.EntitlementDetailSerializer, punter.entitlement_details.all())

    @action(methods=['GET'])
    def tickets(self, request, pk=None):
        punter = self.get_object()
        return serialize_queryset(self, api_serializers.ComprehensiveTicketSerializer, punter.tickets.all())

class EntitlementViewSet(viewsets.ModelViewSet):
    queryset = models.Entitlement.objects.all()
    serializer_class = api_serializers.EntitlementSerializer

class EntitlementDetailViewSet(viewsets.ModelViewSet):
    queryset = models.EntitlementDetail.objects.all()
    serializer_class = api_serializers.EntitlementDetailSerializer

class FilmViewSet(viewsets.ModelViewSet):
    queryset = models.Film.objects.all()
    serializer_class = api_serializers.FilmSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description')

    @action()
    def update_remote(self, request, pk=None):
        film = self.get_object()
        film.update_remote()
        film.save()
        return Response(api_serializers.FilmSerializer(film).data)

    @top_level_action(methods=['get'])
    def search_tmdb(self, request, pk=None):
        results = models.Film.search_tmdb(request.GET.get('query'))
        results = api_serializers.FilmSerializer(results, many=True).data
        return Response(results)

    @action(methods=['GET'])
    def showings(self, request, pk=None):
        film = self.get_object()
        return serialize_queryset(self, api_serializers.GroupedShowingSerializer, film.showings.all())

class ShowingViewSet(viewsets.ModelViewSet):
    queryset = models.Showing.objects.all()
    serializer_class = api_serializers.ShowingSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('film__name',)

class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = api_serializers.EventSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(methods=['GET'])
    def showings(self, request, pk=None):
        event = self.get_object()
        return serialize_queryset(self, api_serializers.ShowingSerializer, event.showings.all())

    @action(methods=['GET'])
    def tickettypes(self, request, pk=None):
        event = self.get_object()
        return serialize_queryset(self, api_serializers.TicketTypeSerializer, event.tickettype_set.all())

    @action(methods=['POST'])
    def reset_ticket_types_by_event_type(self, request, pk=None):
        event = self.get_object()
        event.tickettype_set.all().delete()
        event.create_ticket_types_by_event_types()
        return Response(self.serializer_class(event).data)
