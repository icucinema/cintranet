from PyQt5 import QtCore
from ticketing import models

__author__ = 'lukegb'

def punter_name(punter):
    return models.Punter.pretty_name(punter)

class EventsModel(QtCore.QAbstractListModel):
    NAME_ROLE = QtCore.Qt.UserRole + 1
    EVENT_ID_ROLE = QtCore.Qt.UserRole + 2
    SOLD_TICKETS_ROLE = QtCore.Qt.UserRole + 3

    def __init__(self, events, parent=None):
        super(EventsModel, self).__init__(parent)
        self._data = list(events)

        # register keys
        keys = {
            EventsModel.NAME_ROLE: 'name',
            EventsModel.EVENT_ID_ROLE: 'eventId',
            EventsModel.SOLD_TICKETS_ROLE: 'soldTickets'
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

        event = self._data[index.row()]

        if role == EventsModel.NAME_ROLE:
            return event.name
        elif role == EventsModel.EVENT_ID_ROLE:
            return str(event.id)
        elif role == EventsModel.SOLD_TICKETS_ROLE:
            return int(models.Ticket.objects.filter(ticket_type__event=event, status='live').count())
        else:
            return None

    def refresh(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()


class SearchingEventsModel(EventsModel):
    def __init__(self, base_qs, *args, **kwargs):
        super(SearchingEventsModel, self).__init__(*args, **kwargs)

        self._base_qs = base_qs
        self._data = []

    def refresh(self, **kwargs):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self._data = self._base_qs.filter(**kwargs)
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()


class EditableEventsModel(EventsModel):
    def __init__(self, base_qs, *args, **kwargs):
        super(EditableEventsModel, self).__init__(*args, **kwargs)

        self._base_qs = base_qs
        self._pks = set()
        self._data = []

    @QtCore.pyqtSlot(str)
    def add_item(self, pk):
        pk = int(pk)
        if pk in self._pks:
            return
        self._pks.add(pk)

        p = QtCore.QModelIndex()
        self.beginInsertRows(p, len(self._data), len(self._data))
        self._data.append(self._base_qs.get(id=pk))
        self.endInsertRows()

    @QtCore.pyqtSlot(str)
    def remove_item(self, pk):
        pk = int(pk)
        if pk not in self._pks:
            return
        self._pks.remove(pk)

        idx = 0
        for item in self._data:
            if item.pk == pk:
                break
            idx += 1
        else:
            return

        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, idx, idx)
        self._data.pop(idx)
        self.endRemoveRows()

    def empty(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data))
        d = self._data
        self._pks = set()
        self._data = []
        self.endRemoveRows()
        return [z.pk for z in d]

    def get_pks(self):
        return [z.pk for z in self._data]


class TicketTypesModel(QtCore.QAbstractListModel):
    NAME_ROLE = QtCore.Qt.UserRole + 1
    BGCOLOR_ROLE = QtCore.Qt.UserRole + 2
    EVENT_ID_ROLE = QtCore.Qt.UserRole + 3
    TICKET_ID_ROLE = QtCore.Qt.UserRole + 4
    SALEPRICE_ROLE = QtCore.Qt.UserRole + 5
    APPLICABLE_ROLE = QtCore.Qt.UserRole + 6
    EVENT_NAME_ROLE = QtCore.Qt.UserRole + 7
    SOLD_TICKETS_ROLE = QtCore.Qt.UserRole + 8

    def __init__(self, parent=None):
        super(TicketTypesModel, self).__init__(parent)

        self.use_colours = [
            "#f47e7d", "#b5d045", "#81c0c5", "#e0c7a8"
        ]
        self.next_colour = 0
        self.available_items = []
        self.cheapest_items = []
        self.punter = None

        # register keys
        keys = {
            TicketTypesModel.NAME_ROLE: 'name', TicketTypesModel.BGCOLOR_ROLE: 'bgColor',
            TicketTypesModel.EVENT_ID_ROLE: 'eventId', TicketTypesModel.TICKET_ID_ROLE: 'ticketId',
            TicketTypesModel.SALEPRICE_ROLE: 'salePrice', TicketTypesModel.APPLICABLE_ROLE: 'applicable',
            TicketTypesModel.EVENT_NAME_ROLE: 'eventName', TicketTypesModel.SOLD_TICKETS_ROLE: 'soldTickets'
        }
        self._role_names = keys

    def roleNames(self):
        return self._role_names

    def rowCount(self, index):
        return len(self._data)

    def data(self, index, role):
        if len(self.cheapest_items) == 0:
            self.update_cheapest_items()

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
            return int(ticketType.sale_price_for_punter(self.punter) * 100)
        elif role == TicketTypesModel.APPLICABLE_ROLE:
            return self.get_suggested_opacity(ticketType)
        elif role == TicketTypesModel.EVENT_NAME_ROLE:
            return ticketType.event.name
        elif role == TicketTypesModel.SOLD_TICKETS_ROLE:
            return int(ticketType.tickets.filter(status='live').count())
        else:
            return None

    def refresh(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()

    def get_suggested_opacity(self, item):
        if item not in self.available_items and not item.general_availability:
            return 0.2
        elif item not in self.cheapest_items:
            return 0.55
        return 1

    def update_cheapest_items(self):
        cheapest_price = None
        possible_items = []
        for item in self._data:
            if item not in self.available_items and not item.general_availability:
                continue
            possible_items.append(item)
            sp = item.sale_price_for_punter(self.punter)
            if cheapest_price is None or sp < cheapest_price:
                cheapest_price = sp

        cheapest_options = []
        for item in possible_items:
            if item.sale_price_for_punter(self.punter) == cheapest_price:
                cheapest_options.append(item)
        self.cheapest_items = cheapest_options

    def set_punter(self, punter, available_items=[]):
        self.punter = punter
        self.available_items = available_items
        self.update_cheapest_items()
        self.refresh()


class FilterableTicketTypesModel(TicketTypesModel):
    def __init__(self, ticket_types, parent=None):
        self._core_data = list(ticket_types)
        self._data = []
        super(FilterableTicketTypesModel, self).__init__(parent)

    def filter(self, event_id):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self._data = []
        self.endRemoveRows()
        new_data = [d for d in self._core_data if str(d.event.id) == event_id]
        self.beginInsertRows(p, 0, len(new_data) - 1)
        self._data = new_data
        self.update_cheapest_items()
        self.endInsertRows()


class EditableTicketTypesModel(TicketTypesModel):
    def __init__(self, parent=None):
        self._data = []
        super(EditableTicketTypesModel, self).__init__(parent)

    def add_item(self, item):
        p = QtCore.QModelIndex()
        self.beginInsertRows(p, len(self._data), len(self._data))
        self._data.append(item)
        self.update_cheapest_items()
        self.endInsertRows()

    def remove_item(self, idx):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, idx, idx)
        self._data.pop(idx)
        self.update_cheapest_items()
        self.endRemoveRows()

    def empty(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        d = self._data
        self._data = []
        self.update_cheapest_items()
        self.endRemoveRows()
        return d

    @QtCore.pyqtSlot(result=int)
    def totalPrice(self):
        return int(sum([z.sale_price * 100 for z in self._data]))


class TicketsModel(QtCore.QAbstractListModel):
    ID_ROLE = QtCore.Qt.UserRole + 1
    PUNTER_NAME_ROLE = QtCore.Qt.UserRole + 2
    TIMESTAMP_ROLE = QtCore.Qt.UserRole + 3
    TICKET_TYPE_NAME_ROLE = QtCore.Qt.UserRole + 4

    def __init__(self, parent=None):
        super(TicketsModel, self).__init__(parent)
        self._data = []

        # register keys
        keys = {
            TicketsModel.ID_ROLE: 'id',
            TicketsModel.PUNTER_NAME_ROLE: 'punter_name',
            TicketsModel.TIMESTAMP_ROLE: 'timestamp',
            TicketsModel.TICKET_TYPE_NAME_ROLE: 'ticket_type_name'
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

        ticket = self._data[index.row()]

        if role == TicketsModel.ID_ROLE:
            return ticket.id
        elif role == TicketsModel.PUNTER_NAME_ROLE:
            return punter_name(ticket.punter)
        elif role == TicketsModel.TIMESTAMP_ROLE:
            return ticket.timestamp.isoformat()
        elif role == TicketsModel.TICKET_TYPE_NAME_ROLE:
            return ticket.ticket_type.name
        else:
            return None

    def refresh(self):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()

    def load(self, **kwargs):
        p = QtCore.QModelIndex()
        self.beginRemoveRows(p, 0, len(self._data) - 1)
        self.endRemoveRows()
        self._data = models.Ticket.objects.filter(**kwargs).order_by('-pk')
        self.beginInsertRows(p, 0, len(self._data) - 1)
        self.endInsertRows()