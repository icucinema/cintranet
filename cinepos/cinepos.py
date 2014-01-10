import sys

from PyQt5 import QtCore, QtGui, QtQuick, QtWidgets
from cintranet.ticketing import models
from django.db.models import Q

__author__ = 'lukegb'

class EventsModel(QtCore.QAbstractListModel):
    NAME_ROLE = QtCore.Qt.UserRole + 1
    EVENT_ID_ROLE = QtCore.Qt.UserRole + 2

    def __init__(self, events, parent=None):
        super(EventsModel, self).__init__(parent)
        self._data = list(events)

        # register keys
        keys = {EventsModel.NAME_ROLE: 'name', EventsModel.EVENT_ID_ROLE: 'eventId'}
        self._role_names = keys

    def roleNames(self):
        return self._role_names

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None

        if index.row() > len(self._data):
            return None

        event = self._data[index.row()]

        if role == EventsModel.NAME_ROLE:
            return event.name
        elif role == EventsModel.EVENT_ID_ROLE:
            return str(event.id)
        else:
            return None

class TicketTypesModel(QtCore.QAbstractListModel):
    NAME_ROLE = QtCore.Qt.UserRole + 1
    BGCOLOR_ROLE = QtCore.Qt.UserRole + 2
    EVENT_ID_ROLE = QtCore.Qt.UserRole + 3
    TICKET_ID_ROLE = QtCore.Qt.UserRole + 4
    SALEPRICE_ROLE = QtCore.Qt.UserRole + 5
    APPLICABLE_ROLE = QtCore.Qt.UserRole + 6
    EVENT_NAME_ROLE = QtCore.Qt.UserRole + 7

    def __init__(self, parent=None):
        super(TicketTypesModel, self).__init__(parent)

        self.use_colours = [
            "#f47e7d", "#b5d045", "#81c0c5", "#e0c7a8"
        ]
        self.next_colour = 0

        # register keys
        keys = {
            TicketTypesModel.NAME_ROLE: 'name', TicketTypesModel.BGCOLOR_ROLE: 'bgColor',
            TicketTypesModel.EVENT_ID_ROLE: 'eventId', TicketTypesModel.TICKET_ID_ROLE: 'ticketId',
            TicketTypesModel.SALEPRICE_ROLE: 'salePrice', TicketTypesModel.APPLICABLE_ROLE: 'applicable',
            TicketTypesModel.EVENT_NAME_ROLE: 'eventName'
        }
        self._role_names = keys

    def roleNames(self):
        return self._role_names

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        if not index.isValid():
            return None

        if index.row() > len(self._data):
            return None

        ticketType = self._data[index.row()]

        if role == TicketTypesModel.NAME_ROLE:
            return ticketType.name
        elif role == TicketTypesModel.BGCOLOR_ROLE:
            c = self.use_colours[self.next_colour]
            self.next_colour = (self.next_colour + 1) % len(self.use_colours)
            return c
        elif role == TicketTypesModel.EVENT_ID_ROLE:
            return str(ticketType.event.id)
        elif role == TicketTypesModel.TICKET_ID_ROLE:
            return str(ticketType.id)
        elif role == TicketTypesModel.SALEPRICE_ROLE:
            return int(ticketType.sale_price * 100)
        elif role == TicketTypesModel.APPLICABLE_ROLE:
            #return ticketType in self.get_cheapest_options()
            return self.get_suggested_opacity(ticketType)
        elif role == TicketTypesModel.EVENT_NAME_ROLE:
            return ticketType.event.name
        else:
            return None

    def refresh(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()

    def get_suggested_opacity(self, item):
        if item.pk not in self.available_items and not item.general_availability:
            return 0.2
        elif item not in self.get_cheapest_items():
            return 0.55
        return 1

    def get_cheapest_items(self):
        cheapest_price = None
        possible_items = []
        for item in self._data:
            if item.pk not in self.available_items and not item.general_availability:
                continue
            possible_items.append(item)
            if cheapest_price is None or item.sale_price < cheapest_price:
                cheapest_price = item.sale_price

        cheapest_options = []
        for item in possible_items:
            if item.sale_price == cheapest_price:
                cheapest_options.append(item)
        return cheapest_options

    def set_punter(self, punter, available_items=[]):
        self.punter = punter
        self.available_items = [a.pk for a in available_items]
        self.refresh()

class FilterableTicketTypesModel(TicketTypesModel):
    def __init__(self, ticket_types, parent=None):
        self._core_data = list(ticket_types)
        self._data = []
        super(FilterableTicketTypesModel, self).__init__(parent)

    def filter(self, event_id):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data))
        self._data = []
        self.endRemoveRows()
        new_data = [d for d in self._core_data if str(d.event.id) == event_id]
        self.beginInsertRows(p, 0, len(new_data) - 1)
        self._data = new_data
        self.endInsertRows()

class EditableTicketTypesModel(TicketTypesModel):
    def __init__(self, parent=None):
        self._data = []
        super(EditableTicketTypesModel, self).__init__(parent)

    def add_item(self, item):
        p = QtCore.QModelIndex()
        self.beginInsertRows(p, len(self._data), len(self._data))
        self._data.append(item)
        self.endInsertRows()

    def remove_item(self, idx):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, idx, idx)
        self._data.pop(idx)
        self.endRemoveRows()

    def empty(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data))
        d = self._data
        self._data = []
        self.endRemoveRows()
        return d

    @QtCore.pyqtSlot(result=int)
    def totalPrice(self):
        return int(sum([z.sale_price * 100 for z in self._data]))


class CineposApplication(QtWidgets.QApplication):
    def __init__(self, event_ids, *args, **kwargs):
        super(CineposApplication, self).__init__(*args, **kwargs)

        self.event_ids = event_ids
        self.current_punter = None

        self.setup_models()
        self.setup_view()
        self.wire_view()
        self.set_punter(None)
        self.prepare_view()

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


        self.context.setContextProperty('unknownPunter', False)
        self.context.setContextProperty('acquiringPunterData', True)

    def prepare_view(self):
        self.view.setSource(QtCore.QUrl('cinepos/ui/ui.qml'))
        self.rootObj = self.view.rootObject()

        # wire slots
        self.rootObj.changedCurrentEvent.connect(self.on_event_changed)
        self.rootObj.gotPunterIdentifier.connect(self.on_new_punter_identifier)
        self.rootObj.addedToCart.connect(self.on_added_to_cart)
        self.rootObj.removedFromCart.connect(self.on_removed_from_cart)
        self.rootObj.saleCompleted.connect(self.on_sale_completed)
        self.rootObj.saleVoided.connect(self.on_sale_voided)
        self.rootObj.cardLinkPerformed.connect(self.on_card_link_performed)

        # final init!
        self.tickettypes_model.filter(str(self.event_ids[0]))
        self.rootObj.setCurrentEvent(str(self.event_ids[0]))

        # and show the view
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
        try:

            print "Found punter by", identifier_type, ":", identifier
            print punter
            self.set_punter(punter)
        except models.Punter.DoesNotExist:
            print "Could not find punter by", identifier_type, ":", identifier
            if identifier_type == 'swipecard':
                self.get_cid_for_swipecard(identifier)
            else:
                self.unknown_punter()
            self.set_punter(None)

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

    def on_sale_voided(self):
        self.cart_model.empty()
        self.set_punter(None)

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

if __name__ == '__main__':
    app = CineposApplication([7,8,9], sys.argv)
    app.exec_()
    # view = QtQuick.QQuickView()
    # context = view.rootContext()
    # event_ids = [7, 8, 9]
    # events_to_load = models.Event.objects.filter(id__in=event_ids)
    # eventsModel = EventsModel(events_to_load)
    # tickettypes_to_load = models.TicketType.objects.filter(event__id__in=event_ids)
    # ticketTypesModel = TicketTypesModel(tickettypes_to_load)
    # context.setContextProperty('ticketSelectionModel', ticketTypesModel)
    # context.setContextProperty('eventsModel', eventsModel)
    # evh = EventHandler()
    # view.setSource(QtCore.QUrl('cinepos/ui/ui.qml'))
    # evh.connect_triggers(view.rootObject())
    # view.show()
    # app.exec_()