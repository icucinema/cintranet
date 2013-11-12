from rest_framework import viewsets

from . import models, api_serializers

class PunterViewSet(viewsets.ModelViewSet):
    queryset = models.Punter.objects.all()
    serializer_class = api_serializers.PunterSerializer
    filter_fields = ('punter_type',)

    def list(self, request, *args, **kwargs):
        self.serializer_class = api_serializers.FlatPunterSerializer
        return super(PunterViewSet, self).list(request, *args, **kwargs)