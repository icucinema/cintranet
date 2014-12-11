from rest_framework import viewsets, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from . import models, api_serializers

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
    serializer_class = api_serializers.ComprehensiveTicketSerializer
    filter_fields = ('event',)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)

class EventTypeViewSet(viewsets.ModelViewSet):
    queryset = models.EventType.objects.all()
    serializer_class = api_serializers.EventTypeSerializer

class ShowingsWeekViewSet(viewsets.ModelViewSet):
    queryset = models.ShowingsWeek.objects.all()
    serializer_class = api_serializers.ShowingsWeekSerializer

class PunterViewSet(viewsets.ModelViewSet):
    queryset = models.Punter.objects.all()
    serializer_class = api_serializers.PunterSerializer
    filter_fields = ('punter_type',)
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'cid', 'login', 'email')

    def list(self, request, *args, **kwargs):
        return super(PunterViewSet, self).list(request, *args, **kwargs)

    @detail_route(methods=['GET'])
    def entitlement_details(self, request, pk=None):
        punter = self.get_object()
        return serialize_queryset(self, api_serializers.EntitlementDetailSerializer, punter.entitlement_details.all())

    @detail_route(methods=['GET'])
    def tickets(self, request, pk=None):
        punter = self.get_object()
        return serialize_queryset(self, api_serializers.ComprehensiveTicketSerializer, punter.tickets.all())

class PunterIdentifierViewSet(viewsets.ModelViewSet):
    queryset = models.PunterIdentifier.objects.all()
    serializer_class = api_serializers.PunterIdentifierSerializer

class EntitlementViewSet(viewsets.ModelViewSet):
    queryset = models.Entitlement.objects.all()
    serializer_class = api_serializers.EntitlementSerializer

class EntitlementDetailViewSet(viewsets.ModelViewSet):
    queryset = models.EntitlementDetail.objects.all()
    serializer_class = api_serializers.EntitlementDetailSerializer

class DistributorViewSet(viewsets.ModelViewSet):
    queryset = models.Distributor.objects.all()
    serializer_class = api_serializers.DistributorSerializer

    @detail_route(methods=['GET'])
    def films(self, request, pk=None):
        distributor = self.get_object()
        return serialize_queryset(self, api_serializers.FilmSerializer, distributor.films.all())

class FilmViewSet(viewsets.ModelViewSet):
    queryset = models.Film.objects.all()
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name', 'description')

    serializer_class = api_serializers.FilmSerializer

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class
        return api_serializers.FlatFilmSerializer

    @detail_route()
    def update_remote(self, request, pk=None):
        film = self.get_object()
        film.update_remote()
        film.save()
        return Response(api_serializers.FilmSerializer(film).data)

    @list_route(methods=['get'])
    def search_tmdb(self, request, pk=None):
        results = models.Film.search_tmdb(request.GET.get('query'))
        results = api_serializers.FilmSerializer(results, many=True).data
        return Response(results)

    @detail_route(methods=['GET'])
    def showings(self, request, pk=None):
        film = self.get_object()
        return serialize_queryset(self, api_serializers.ShowingsWeekSerializer, film.showing_weeks.all())

class ShowingViewSet(viewsets.ModelViewSet):
    queryset = models.Showing.objects.all().extra(select={'sorting_distance': '''
CASE
  WHEN
      ticketing_showing.start_time > NOW()
    THEN
      ticketing_showing.start_time - NOW()
    ELSE
      INTERVAL '@ 1 year' + (NOW() - ticketing_showing.start_time)
  END
    '''}).order_by('sorting_distance')
    serializer_class = api_serializers.ShowingSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('week__film__name',)

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return self.serializer_class
        return api_serializers.FlatShowingSerializer

    @detail_route(methods=['GET'])
    def tickets(self, request, pk=None):
        showing = self.get_object()
        return serialize_queryset(self, api_serializers.ComprehensiveTicketSerializer, showing.tickets())

class EventViewSet(viewsets.ModelViewSet):
    queryset = models.Event.objects.all()
    serializer_class = api_serializers.EventSerializer
    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('name',)

    @detail_route(methods=['GET'])
    def showings(self, request, pk=None):
        event = self.get_object()
        return serialize_queryset(self, api_serializers.ShowingSerializer, event.showings.all())

    @detail_route(methods=['GET'])
    def tickettypes(self, request, pk=None):
        event = self.get_object()
        return serialize_queryset(self, api_serializers.TicketTypeSerializer, event.tickettype_set.all())

    @detail_route(methods=['GET'])
    def tickets(self, request, pk=None):
        event = self.get_object()
        return serialize_queryset(self, api_serializers.ComprehensiveTicketSerializer, event.tickets.all())

    @detail_route(methods=['POST'])
    def reset_ticket_types_by_event_type(self, request, pk=None):
        event = self.get_object()
        event.tickettype_set.all().delete()
        event.create_ticket_types_by_event_types()
        return Response(self.serializer_class(event).data)
