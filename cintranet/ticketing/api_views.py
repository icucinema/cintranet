from rest_framework import viewsets
from rest_framework.decorators import action, link
from rest_framework.response import Response

from . import models, api_serializers

def top_level_action(methods=['post'], **kwargs):
    def decorator(func):
        func.toplevel_bind_to_methods = methods
        func.kwargs = kwargs
        return func
    return decorator

class PunterViewSet(viewsets.ModelViewSet):
    queryset = models.Punter.objects.all()
    serializer_class = api_serializers.PunterSerializer
    filter_fields = ('punter_type',)

    def list(self, request, *args, **kwargs):
        return super(PunterViewSet, self).list(request, *args, **kwargs)

    @action(methods=['GET'])
    def entitlement_details(self, request, pk=None):
        self.serializer_class = api_serializers.EntitlementDetailSerializer
        self.paginate_by = None

        punter = self.get_object()

        self.object_list = punter.entitlement_details.all()
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

    @action(methods=['GET'])
    def tickets(self, request, pk=None):
        self.serializer_class = api_serializers.TicketSerializer
        self.paginate_by = None

        punter = self.get_object()

        self.object_list = punter.tickets.all()
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)

        return Response(serializer.data)

class EntitlementViewSet(viewsets.ModelViewSet):
    queryset = models.Entitlement.objects.all()
    serializer_class = api_serializers.EntitlementSerializer

class EntitlementDetailViewSet(viewsets.ModelViewSet):
    queryset = models.EntitlementDetail.objects.all()
    serializer_class = api_serializers.EntitlementDetailSerializer

class FilmViewSet(viewsets.ModelViewSet):
    queryset = models.Film.objects.all()
    serializer_class = api_serializers.FilmSerializer

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
