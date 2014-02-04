# -*- coding: utf-8 -*-

import datetime

from PyQt5 import QtWidgets, QtQuick, QtCore, QtGui
from ticketing import models, api_serializers
from django.db.models import Q
from django.utils.timezone import now

from .qtmodels import EventsModel, FilterableTicketTypesModel, EditableTicketTypesModel, SearchingEventsModel, \
    EditableEventsModel, TicketsModel, punter_name

__author__ = 'lukegb'

back_range = datetime.timedelta(minutes=60)
forward_range = datetime.timedelta(minutes=12 * 60)


def flatten_element(v):
    if isinstance(v, dict):
        return flatten_to_dict(v)
    elif isinstance(v, list):
        return flatten_to_list(v)
    elif isinstance(v, datetime.datetime):
        return str(v.isoformat())
    else:
        return v


def flatten_to_list(pl):
    return [flatten_element(v) for v in pl]


def flatten_to_dict(pd):
    d = {}
    for k, v in pd.iteritems():
        d[k] = flatten_element(v)
    return d


class CineposApplication(QtGui.QGuiApplication):
    def __init__(self, args, hw_interface,
                 view_location='ui/ui.qml', full_screen=False, window_title='CinePoS', window_icon=None):
        super(CineposApplication, self).__init__(args)

        nownow = now()
        self.now_date = nownow.replace(hour=0, minute=5, second=0)
        min_between = nownow - back_range
        max_between = nownow + forward_range
        self.event_ids = models.Event.objects.filter(
            start_time__gt=min_between, start_time__lt=max_between
        ).values_list('id', flat=True)
        self.event_ids = []
        self.hw_interface = hw_interface
        self.view_location = view_location
        self.current_punter = None
        self.full_screen = full_screen
        self.window_title = window_title
        self.window_icon = window_icon

        self.setup_event_select_models()
        self.setup_models()
        self.setup_view()
        self.wire_view()
        self.set_punter(None)
        self.prepare_view()

    def set_event_ids(self, event_ids):
        self.event_ids = event_ids

        self.setup_models()
        self.wire_view()

        if len(self.event_ids) > 0:
            self.tickettypes_model.filter(str(self.event_ids[0]))
            self.rootObj.setCurrentEvent(str(self.event_ids[0]))

    def setup_event_select_models(self):
        self.event_search_model = SearchingEventsModel(base_qs=models.Event.objects.all(), events=[])
        self.event_select_model = EditableEventsModel(base_qs=models.Event.objects.all(), events=[])
        [self.event_select_model.add_item(n) for n in self.event_ids]

    def setup_models(self):
        self.events = models.Event.objects.filter(id__in=self.event_ids)
        self.events_model = EventsModel(self.events)

        self.tickettypes = models.TicketType.objects.filter(event__id__in=self.event_ids).order_by(
            'sale_price', '-name'
        )
        self.tickettypes_model = FilterableTicketTypesModel(self.tickettypes)
        self.cart_model = EditableTicketTypesModel()
        self.tickets_listing_model = TicketsModel()

    def setup_view(self):
        self.view = QtQuick.QQuickView()
        self.view.setTitle(self.window_title)
        if self.window_icon is not None:
            self.view.setIcon(QtGui.QIcon(self.window_icon))
        self.view.setResizeMode(self.view.SizeRootObjectToView)
        self.context = self.view.rootContext()

    def wire_view(self):
        # wire context properties
        self.context.setContextProperty('ticketSelectionModel', self.tickettypes_model)
        self.context.setContextProperty('ticketsListingModel', self.tickets_listing_model)
        self.context.setContextProperty('eventsModel', self.events_model)
        self.context.setContextProperty('cartModel', self.cart_model)
        self.context.setContextProperty('eventSearchModel', self.event_search_model)
        self.context.setContextProperty('eventSelectedModel', self.event_select_model)

    def prepare_view(self):
        self.view.setSource(QtCore.QUrl(self.view_location))
        self.rootObj = self.view.rootObject()

        # wire slots
        self.rootObj.changedCurrentEvent.connect(self.on_event_changed)
        self.rootObj.gotPunterIdentifier.connect(self.on_new_punter_identifier)
        self.rootObj.addedToCart.connect(self.on_added_to_cart)
        self.rootObj.removedFromCart.connect(self.on_removed_from_cart)
        self.rootObj.saleCompleted.connect(self.on_sale_completed)
        self.rootObj.saleNoSaled.connect(self.on_sale_no_saled)
        self.rootObj.cardLinkPerformed.connect(self.on_card_link_performed)
        self.rootObj.updateEventListing.connect(self.on_update_event_listing)
        self.rootObj.eventsSelected.connect(self.on_events_selected)
        self.rootObj.selectEventsCancelled.connect(self.on_select_events_cancelled)
        self.rootObj.ticketDetailsRequested.connect(self.on_ticket_details_requested)
        self.rootObj.voidTicketRequested.connect(self.on_void_ticket)
        self.rootObj.refundTicketRequested.connect(self.on_refund_ticket)
        self.rootObj.reprintTicketRequested.connect(self.on_reprint_ticket)
        self.rootObj.salesReportRequested.connect(self.on_sales_report_requested)
        self.rootObj.ticketsForPunterRequested.connect(self.on_tickets_for_punter_requested)
        self.rootObj.lastSoldTicketsRequested.connect(self.on_last_sold_tickets_requested)

        # final init!
        if len(self.event_ids) > 0:
            self.tickettypes_model.filter(str(self.event_ids[0]))
            self.rootObj.setCurrentEvent(str(self.event_ids[0]))
        else:
            self.rootObj.doSelectEvents()

        # and show the view
        if self.full_screen:
            self.view.showFullScreen()
        else:
            self.view.showMaximized()

    def set_punter(self, punter):
        self.current_punter = punter
        self.context.setContextProperty('punterName', punter_name(punter))

        if punter is None:
            available_items = []
        else:
            available_items = punter.available_tickets(events=models.Event.objects.filter(id__in=self.event_ids), at_time=self.now_date)

        self.tickettypes_model.set_punter(punter, available_items)
        self.cart_model.set_punter(punter, available_items)

    def on_event_changed(self, new_event_id):
        self.tickettypes_model.filter(new_event_id)

    def on_new_punter_identifier(self, identifier_type, identifier):
        if identifier_type != 'unknown':
            qs = models.Punter.objects.filter(**{
                identifier_type: identifier
            })
        else:
            qs = models.Punter.objects.filter(
                Q(cid=identifier) | Q(name__iexact=identifier) | Q(login__iexact=identifier) | Q(
                    email__iexact=identifier)
            )
        try:
            punter = qs.get()
        except models.Punter.DoesNotExist:
            print "Could not find punter by", identifier_type, ":", identifier
            if identifier_type == 'swipecard':
                self.get_cid_for_swipecard(identifier)
            else:
                self.unknown_punter()
            self.set_punter(None)
            return
        except models.Punter.MultipleObjectsReturned:
            if identifier_type == 'unknown':
                ordering = ['cid', 'name__iexact', 'login__iexact', 'email__iexact']
                for thing in ordering:
                    try:
                        punter = models.Punter.objects.get(**{thing: identifier})
                        break
                    except models.Punter.DoesNotExist:
                        continue
                    except models.Punter.MultipleObjectsReturned:
                        print "WTF? Too many punters with", thing, "as", identifier, "!"
                        return
            else:
                return

        print "Found punter by", identifier_type, ":", identifier
        print punter
        self.set_punter(punter)

    def on_added_to_cart(self, ticket_id):
        for tickettype in self.tickettypes:
            if str(tickettype.id) == ticket_id:
                found_tickettype = tickettype
                break
        else:
            return

        self.cart_model.add_item(found_tickettype)

    def on_removed_from_cart(self, index):
        self.cart_model.remove_item(index)

    def on_sale_completed(self):
        data = self.cart_model.empty()
        total_cost = 0
        for tickettype in data:
            total_cost += int(tickettype.sale_price_for_punter(self.current_punter) * 100)
        if total_cost > 0:
            print "Opening cash drawer!"
            self.hw_interface.cashdrawer.open()
        for tickettype in data:
            self.generate_ticket(tickettype)
        self.events_model.refresh()
        self.set_punter(None)

    def on_sale_no_saled(self):
        if len(self.cart_model.empty()) == 0:
            # cart was already empty - open the cash drawer instead of emptying the cart
            print "Opening cash drawer!"
            self.hw_interface.cashdrawer.open()
        self.set_punter(None)

    def on_events_selected(self):
        self.set_event_ids(self.event_select_model.get_pks())
        if len(self.event_ids) == 0:
            self.show_dialog(
                type_='error',
                title='Event selection required',
                message='At least one event must be selected.',
                button='OK', button_target='eventselect'
            )

    def on_select_events_cancelled(self):
        if len(self.event_ids) == 0:
            self.quit()

    def on_ticket_details_requested(self, ticket_id):
        try:
            ticket = models.Ticket.objects.get(pk=ticket_id)
            self.rootObj.ticketDetailsRetrieved(
                flatten_to_dict(api_serializers.ComprehensiveTicketSerializer(ticket).data)
            )
        except models.Ticket.DoesNotExist:
            self.show_dialog(
                type_='error',
                title='Ticket not found',
                message='A ticket with the ID {} could not be found.'.format(ticket_id),
                button='OK', button_target='viewticket'
            )

    def on_card_link_performed(self, cid):
        punter, created = models.Punter.objects.get_or_create(cid=cid, defaults={
            'swipecard': self.acquiring_swipecard
        })
        if not created:
            punter.swipecard = self.acquiring_swipecard
            punter.save()
            print "Saving swipecard into existing punter", punter
        else:
            print "Created new punter for swipecard", punter
        self.set_punter(punter)

    def on_update_event_listing(self, date):
        day_in_question = datetime.datetime.strptime(date, "%d/%m/%Y")
        next_day = day_in_question.replace(day=day_in_question.day + 1, hour=0, minute=0, second=0)
        self.now_date = day_in_question.replace(hour=0, minute=5, second=0)
        self.event_search_model.refresh(start_time__gte=day_in_question, start_time__lt=next_day)

    def on_refund_ticket(self, ticket_id):
        try:
            ticket = models.Ticket.objects.get(pk=ticket_id)
            self.hw_interface.cashdrawer.open()
            ticket.refund()
            ticket.save()
            self.on_ticket_details_requested(ticket_id)
            self.show_dialog(
                type_='info',
                title='Ticket refunded',
                message='Please refund £{}.'.format(ticket.ticket_type.sale_price),
                button='OK', button_target='ticketdetails'
            )
        except models.Ticket.DoesNotExist:
            self.show_dialog(
                type_='error',
                title='Ticket not found',
                message='A ticket with the ID {} could not be found.'.format(ticket_id),
                button='OK', button_target='viewticket'
            )

    def on_reprint_ticket(self, ticket_id):
        try:
            ticket = models.Ticket.objects.get(pk=ticket_id)
            self.hw_interface.printer.print_ticket(ticket)
        except models.Ticket.DoesNotExist:
            self.show_dialog(
                type_='error',
                title='Ticket not found',
                message='A ticket with the ID {} could not be found.'.format(ticket_id),
                button='OK', button_target='viewticket'
            )

    def on_void_ticket(self, ticket_id):
        try:
            ticket = models.Ticket.objects.get(pk=ticket_id)
            ticket.void()
            ticket.save()
            self.on_ticket_details_requested(ticket_id)
        except models.Ticket.DoesNotExist:
            self.show_dialog(
                type_='error',
                title='Ticket not found',
                message='A ticket with the ID {} could not be found.'.format(ticket_id),
                button='OK', button_target='viewticket'
            )

    def on_sales_report_requested(self):
        self.show_dialog(
            type_='info',
            title='Printing...',
            message='Now printing sales report',
            button='OK', button_target=''
        )
        self.generate_report()

    def show_dialog(self, type_, title, message, button='OK', button_target=''):
        self.rootObj.showDialog({
            'type': type_,
            'title': title,
            'message': message,
            'button': button,
            'button_target': button_target
        })

    def get_cid_for_swipecard(self, swipecard):
        self.acquiring_swipecard = swipecard
        self.rootObj.doCardLink()

    def unknown_punter(self):
        self.rootObj.unknownPunterQueried()

    def generate_ticket(self, tickettype):
        # here goes the magic!
        punter = self.current_punter

        ticket = models.Ticket.generate(ticket_type=tickettype, punter=punter)
        ec = self.event_ids_to_char[tickettype.event_id]
        self.hw_interface.printer.print_ticket(ticket, ec)

    def generate_report(self):
        # this is going to be interesting...
        events = models.Event.objects.filter(id__in=self.event_ids)

        self.hw_interface.printer.print_report(events)

    def on_tickets_for_punter_requested(self):
        self.tickets_listing_model.load(punter=self.current_punter)
        self.loaded_ticket_listing("Tickets for: {}".format(punter_name(self.current_punter)))

    def on_last_sold_tickets_requested(self):
        self.tickets_listing_model.load(ticket_type__event__in=self.events)
        self.loaded_ticket_listing("Last Sold Tickets")

    def loaded_ticket_listing(self, title=None):
        self.rootObj.ticketListRetrieved(title)
