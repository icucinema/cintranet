import datetime

from PyQt5 import QtWidgets, QtQuick, QtCore
from cintranet.ticketing import models
from django.db.models import Q
from django.utils.timezone import now

from .qtmodels import EventsModel, FilterableTicketTypesModel, EditableTicketTypesModel, SearchingEventsModel, EditableEventsModel

__author__ = 'lukegb'

back_range = datetime.timedelta(minutes=60)
forward_range = datetime.timedelta(minutes=6*60)

class CineposApplication(QtWidgets.QApplication):
    def __init__(self, args, view_location='ui/ui.qml', full_screen=False):
        super(CineposApplication, self).__init__(args)

        nownow = now()
        min_between = nownow - back_range
        max_between = nownow + forward_range
        self.event_ids = models.Event.objects.filter(
            start_time__gt=min_between, start_time__lt=max_between
        ).values_list('id', flat=True)
        self.view_location = view_location
        self.current_punter = None
        self.full_screen = full_screen

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

    def setup_view(self):
        self.view = QtQuick.QQuickView()
        self.view.setResizeMode(self.view.SizeRootObjectToView)
        self.context = self.view.rootContext()

    def wire_view(self):
        # wire context properties
        self.context.setContextProperty('ticketSelectionModel', self.tickettypes_model)
        self.context.setContextProperty('eventsModel', self.events_model)
        self.context.setContextProperty('cartModel', self.cart_model)
        self.context.setContextProperty('eventSearchModel', self.event_search_model)
        self.context.setContextProperty('eventSelectedModel', self.event_select_model)


        self.context.setContextProperty('unknownPunter', False)
        self.context.setContextProperty('acquiringPunterData', True)

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
            self.view.show()

    def set_punter(self, punter):
        self.current_punter = punter
        if punter is None:
            punter_name = 'Guest'
        elif len(punter.name) == 0:
            punter_name = 'Unknown (ID: %d)' % (punter.id,)
        else:
            punter_name = punter.name
        self.context.setContextProperty('punterName', punter_name)

        if punter is None:
            available_items = []
        else:
            available_items = punter.available_tickets(events=models.Event.objects.filter(id__in=self.event_ids))
        self.tickettypes_model.set_punter(punter, available_items)
        self.cart_model.set_punter(punter, available_items)

    def on_event_changed(self, new_event_id):
        self.tickettypes_model.filter(new_event_id)

    def on_new_punter_identifier(self, identifier_type, identifier):
        if identifier_type != 'unknown':
            punter = models.Punter.objects.get(**{
                identifier_type: identifier
            })
        else:
            qs = models.Punter.objects.filter(
                Q(cid=identifier) | Q(name__iexact=identifier) | Q(login__iexact=identifier) | Q(email__iexact=identifier)
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
                ordering = ['cid', 'name__iexact', 'login__iexact', 'email__iexact']
                for thing in ordering:
                    try:
                        punter = models.Punter.objects.get(**{ thing: identifier })
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
        for tickettype in data:
            self.generate_ticket(tickettype)
        self.set_punter(None)

    def on_sale_no_saled(self):
        self.cart_model.empty()
        self.set_punter(None)

    def on_events_selected(self):
        self.set_event_ids(self.event_select_model.get_pks())
        if len(self.event_ids) == 0:
            self.quit()

    def on_select_events_cancelled(self):
        if len(self.event_ids) == 0:
            self.quit()

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
        next_day = day_in_question.replace(day=day_in_question.day+1, hour=0, minute=0, second=0)
        self.event_search_model.refresh(start_time__gte=day_in_question, start_time__lt=next_day)

    def get_cid_for_swipecard(self, swipecard):
        self.acquiring_swipecard = swipecard
        self.rootObj.doCardLink()

    def unknown_punter(self):
        self.rootObj.unknownPunterQueried()

    def generate_ticket(self, tickettype):
        # here goes the magic!
        punter = self.current_punter

        print "GENERATING TICKET OF TYPE", tickettype
        ticket = models.Ticket.generate(ticket_type=tickettype, punter=punter)
        print "TICKET GENERATED", ticket
        print "Was generally available?", tickettype.general_availability
        print "Entitlement?", ticket.entitlement
        try:
            ed = ticket.entitlement.entitlement_details.get(punter=punter)
            print "Entitlement Detail?", ed, ed.remaining_uses
        except:
            pass
        print "PRINTING TICKET"
