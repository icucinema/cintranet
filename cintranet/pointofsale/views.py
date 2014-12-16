from decimal import Decimal
import datetime

from django.shortcuts import render
from django.db.models import Q

import ticketing.models
from . import models, utils

from rest_framework import viewsets, serializers, filters, status
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticketing.models.Ticket

class TicketPrototypeSerializer(serializers.Serializer):
    ticket_type = serializers.PrimaryKeyRelatedField(queryset=ticketing.models.TicketType.objects.all())
    punter = serializers.PrimaryKeyRelatedField(queryset=ticketing.models.Punter.objects.all(), allow_null=True)

class TicketGenerationSerializer(serializers.Serializer):
    tickets = TicketPrototypeSerializer(many=True)
    printer = serializers.PrimaryKeyRelatedField(queryset=models.Printer.objects.all(), allow_null=True)

class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ticketing.models.Ticket.objects.all()
    serializer_class = TicketSerializer

    @list_route(methods=['post'])
    def generate(self, request):
        serializer = TicketGenerationSerializer(data=request.data)
        if serializer.is_valid():
            printer = models.Printer.objects.get(pk=serializer.data['printer']) if serializer.data['printer'] else None
            total_value = Decimal(0)

            tickets = []
            for proto in serializer.data['tickets']:
                ticket_type = ticketing.models.TicketType.objects.get(pk=proto['ticket_type'])
                punter = None if not proto['punter'] else ticketing.models.Punter.objects.get(pk=proto['punter'])
                tickets.append(ticketing.models.Ticket.generate(ticket_type=ticket_type, punter=punter))
                total_value += ticket_type.sale_price

            if printer:
                printer.print_tickets(tickets)
                if total_value > Decimal(0) and request.GET.get('open_cashdrawer', None) == 'true':
                    printer.open_cash_drawer()
            return Response({'status': 'printing', 'tickets': TicketSerializer(tickets, many=True).data})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def void(self, request, pk=None):
        ticket = self.get_object()
        try:
            ticket.void()
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(ticket).data)

    @detail_route(methods=['post'])
    def refund(self, request, pk=None):
        ticket = self.get_object()
        try:
            ticket.refund()
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(ticket).data)

    @detail_route(methods=['post'])
    def collect(self, request, pk=None):
        ticket = self.get_object()
        try:
            ticket.collect()
        except Exception as ex:
            return Response({'error': str(ex)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(TicketSerializer(ticket).data)

class EventSerializer(serializers.ModelSerializer):
    tickets_count = serializers.SerializerMethodField()

    class Meta:
        model = ticketing.models.Event
        fields = ('id', 'name', 'start_time', 'tickets_count')

    def get_tickets_count(self, obj):
        return obj.tickets.filter(status__in=('live', 'pending_collection')).count()

class TicketTypeSerializer(serializers.ModelSerializer):
    allowed = serializers.BooleanField()

    class Meta:
        model = ticketing.models.TicketType

class EventFilterSerializer(serializers.Serializer):
    date = serializers.DateTimeField()

class EventFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        date = request.GET.get('date', None)
        if date is not None:
            serializer = EventFilterSerializer(data=request.GET)
            if serializer.is_valid():
                actual_date = serializer.validated_data['date']
                oneday = datetime.timedelta(days=1, hours=12)
                queryset = queryset.filter(start_time__gt=actual_date, start_time__lte=actual_date+oneday)
            else:
                raise Exception(serializer.errors)

        queryset = queryset.order_by('start_time')

        return queryset

class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ticketing.models.Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = [EventFilterBackend,]

    @detail_route(methods=['get'])
    def ticket_types(self, request, pk=None):
        event = self.get_object()
        queryset = event.tickettype_set.all()
        x = []
        for tt in queryset:
            tt.allowed = tt.general_availability and tt.sell_on_the_door
            x.append(tt)
        serializer = TicketTypeSerializer(x, many=True)
        return Response(serializer.data)

class PunterFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        card_id = request.GET.get('card_id', None)
        if card_id is not None:
            queryset = queryset.filter(identifiers__value=card_id)
            if not queryset.count():
                punter_by_swipe = ticketing.models.Punter.get_by_swipe(card_id)
                if punter_by_swipe:
                    return [punter_by_swipe,]
                else:
                    return []

        search = request.GET.get('search', None)
        if search is not None:
            queryset = queryset.filter(Q(name__icontains=search) | Q(cid=search) | Q(login=search) | Q(email=search))

        return queryset

class PunterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ticketing.models.Punter

class TicketTypeQuerySerializer(serializers.Serializer):
    events = serializers.PrimaryKeyRelatedField(queryset=ticketing.models.Event.objects.all(), many=True)
    timestamp = serializers.DateTimeField()

class PunterViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ticketing.models.Punter.objects.all()
    serializer_class = PunterSerializer
    filter_backends = [PunterFilterBackend,]

    @detail_route(methods=['get'])
    def ticket_types(self, request, pk=None):
        events = ticketing.models.Event.objects.filter(pk__in=request.GET.getlist('events'))
        all_ticket_types = ticketing.models.TicketType.objects.filter(event__in=events)
        sale_point = request.GET['sale_point']
        punter = self.get_object()
        this_ticket_types = punter.available_tickets(events=events, on_door=(sale_point == 'on_door'), online=(sale_point == 'online'))

        tt_dict = dict()
        for tt in all_ticket_types:
            tt_dict[tt.id] = tt
            tt_dict[tt.id].allowed = False
        for tt in this_ticket_types:
            tt_dict[tt.id].allowed = True

        return Response(TicketTypeSerializer(tt_dict.values(), many=True).data)

    @detail_route(methods=['get'])
    def tickets(self, request, pk=None):
        punter = self.get_object()
        detailed_mode = bool(request.GET.get('detailed', None))
        tickets = ticketing.models.Ticket.objects.filter(punter=punter)
        if request.GET.get('status') is not None:
            tickets = tickets.filter(status__in=request.GET.getlist('status'))
        serializer = TicketSerializer if not detailed_mode else DetailedTicketSerializer
        if detailed_mode:
            tickets = tickets.select_related('ticket_type', 'ticket_type__event')
        return Response(serializer(tickets, many=True).data)
        
class PrinterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Printer

class SalesReportJobSerializer(serializers.Serializer):
    events = serializers.PrimaryKeyRelatedField(queryset=ticketing.models.Event.objects.all(), many=True)

class TicketJobSerializer(serializers.Serializer):
    tickets = serializers.PrimaryKeyRelatedField(queryset=ticketing.models.Ticket.objects.all(), many=True)

class PrinterFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        name = request.GET.get('name', None)
        if name:
            queryset = queryset.filter(name=name)
        return queryset

class PrinterViewSet(viewsets.ModelViewSet):
    queryset = models.Printer.objects.all()
    serializer_class = PrinterSerializer
    filter_backends = [PrinterFilterBackend,]

    @detail_route(methods=['post'])
    def print_sales_report(self, request, pk=None):
        printer = self.get_object()
        serializer = SalesReportJobSerializer(data=request.data)
        if serializer.is_valid():
            events = ticketing.models.Event.objects.filter(pk__in=serializer.data['events'])
            printer.print_sales_report(events)
            return Response({'status': 'submitted'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def print_tickets(self, request, pk=None):
        printer = self.get_object()
        serializer = TicketJobSerializer(data=request.data)
        if serializer.is_valid():
            tickets = ticketing.models.Ticket.objects.filter(pk__in=serializer.data['tickets'])
            printer.print_tickets(tickets)
            return Response({'status': 'submitted', 'count': len(serializer.data['tickets'])})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['post'])
    def open_cash_drawer(self, request, pk=None):
        printer = self.get_object()
        printer.open_cash_drawer()
        return Response({'status': 'ding'})

class DetailedTicketTicketTypeSerializer(serializers.ModelSerializer):
    event = EventSerializer()

    class Meta:
        model = ticketing.models.TicketType

class DetailedTicketSerializer(serializers.ModelSerializer):
    ticket_type = DetailedTicketTicketTypeSerializer()

    class Meta:
        model = ticketing.models.Ticket
