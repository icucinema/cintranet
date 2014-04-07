import datetime
import decimal
Decimal = decimal.Decimal

from django.views.generic.base import TemplateView
from django.db.models import Count, Sum
from django.utils.timezone import now

from ticketing import models

def get_default_date_bounds():
    my_now = now()
    start_at = my_now.replace(month=8, day=10, year=my_now.year if my_now.month > 8 else my_now.year - 1)
    end_at = my_now
    return start_at, end_at

def quantize(d, **kwargs):
    return d.quantize(Decimal('.01'), **kwargs)

class IndexView(TemplateView):
    template_name = 'stats/index.html'

class ReportView(TemplateView):
    template_name = 'stats/report.html'

    title = ''
    grouped = False
    data = []
    head = False
    foot = False
    col_classes = []

    def get_head(self, raw_data, data):
        return self.head

    def get_foot(self, raw_data, data):
        return self.foot

    def get_data(self, raw_data):
        return self.data

    def get_col_classes(self, raw_data, data):
        return self.col_classes

    def get_grouped(self, raw_data, data):
        return self.grouped

    def get_title(self, raw_data, data):
        return self.title

    def get_raw_data(self):
        return None

    def get_context_data(self, **kwargs):
        data = {}
        raw_data = self.get_raw_data()
        data['dataset'] = self.get_data(raw_data)
        data['col_classes'] = self.get_col_classes(raw_data, data['dataset'])
        data['title'] = self.get_title(raw_data, data['dataset'])
        data['grouped'] = self.get_grouped(raw_data, data['dataset'])
        data['head'] = zip(self.get_head(raw_data, data['dataset']), data['col_classes'])
        data['foot'] = self.get_foot(raw_data, data['dataset'])
        data.update(super(ReportView, self).get_context_data(**kwargs))
        return data

class OverviewAudiencePlayweekView(ReportView):
    title = 'Audience Overview by Playweek'
    grouped = True
    data = []
    head = ['Film', 'Turnout']

    def get_queryset(self):
        start_at, end_at = get_default_date_bounds()
        return models.Event.objects.all().extra({"playweek": "date_trunc('week', start_time - '4 days'::interval) + '4 days'::interval"}).order_by('playweek').filter(start_time__gt=start_at, start_time__lte=end_at).prefetch_related('showings', 'showings__film')

    def get_raw_data(self):
        events = self.get_queryset()
        ticket_counts = dict(models.Ticket.objects.filter(status='live', ticket_type__event__in=[e.id for e in events]).values('ticket_type__event__id').annotate(count=Count('ticket_type__event__id')).order_by().values_list('ticket_type__event_id', 'count'))

        data = []

        for event in events:
            my_turnout = ticket_counts.get(event.id, 0)
            my_data = {
                'turnout': my_turnout,
                'playweek': event.playweek,
                'date': event.start_time,
                'showings': []
            }
            for showing in event.showings.all():
                my_data['showings'].append({
                    'name': showing.film.name,
                })
            data.append(my_data)

        return data

    def process_raw_playweek(self, current_playweek, current_playweek_data):
        cpd = []
        for name, turnout in current_playweek_data['data'].iteritems():
            cpd.append([
                name,
                turnout
            ])

        return {
            'headings': [current_playweek.strftime('%b. %d %Y'), current_playweek_data['turnout']],
            'data': cpd
        }

    def get_data(self, raw_data):
        # group into playweeks
        playweeks_data = []
        current_playweek = None
        current_playweek_data = None

        for raw_datum in raw_data:
            if current_playweek is None or raw_datum['playweek'] != current_playweek:
                if current_playweek_data is not None:
                    playweeks_data.append(self.process_raw_playweek(current_playweek, current_playweek_data))
                current_playweek = raw_datum['playweek']
                current_playweek_data = {'turnout': 0, 'data': {}}
            current_playweek_data['turnout'] += raw_datum['turnout']
            for showing in raw_datum['showings']:
                current_playweek_data['data'][showing['name']] = raw_datum['turnout'] + current_playweek_data['data'].get(showing['name'], 0)
        playweeks_data.append(self.process_raw_playweek(current_playweek, current_playweek_data))
        return playweeks_data

    def get_foot(self, raw_data, data):
        # sum everything
        total = 0
        for d in data:
            total += d['headings'][-1]
        return ['{} playweeks'.format(len(data)), total]

class OverviewAudienceFilmView(OverviewAudiencePlayweekView):
    grouped = False
    title = 'Audience Overview by Film'

    def get_data(self, raw_data):
        # now group by film
        film_data = {}

        for raw_datum in raw_data:
            for showing in raw_datum['showings']:
                film_data[showing['name']] = film_data.get(showing['name'], 0) + raw_datum['turnout']

        film_data = sorted(film_data.iteritems(), key=lambda fd: fd[0])

        return film_data

    def get_foot(self, raw_data, data):
        total = 0
        for raw_datum in raw_data:
            total += raw_datum['turnout']
        return [None, total]

class OverviewMoneyView(ReportView):
    title = 'Money Overview'
    grouped = True 
    data = []
    head = ['Date', 'Film', 'Take (gross)', 'Refunded (gross)', 'Paid (net)', 'Profit (net)']
    col_classes = ['col-date', None, None, None, None, None]

    def get_raw_data(self):
        start_at, end_at = get_default_date_bounds()
        events = models.Event.objects.all().extra({"playweek": "date_trunc('week', start_time - '4 days'::interval) + '4 days'::interval"}).order_by('playweek').filter(start_time__gt=start_at, start_time__lte=end_at).prefetch_related('showings', 'showings__film')

        event_dicts = []
        showings = {}

        for event in events:
            tickets = event.tickets.exclude(status='void')
            take = tickets.aggregate(take=Sum('ticket_type__sale_price'))['take'] or Decimal(0)
            bor_cost = tickets.exclude(status='refunded').aggregate(bor_cost=Sum('ticket_type__box_office_return_price'))['bor_cost'] or Decimal(0)
            refunded = tickets.filter(status='refunded').aggregate(refunded=Sum('ticket_type__sale_price'))['refunded'] or Decimal(0)
            event_dict = {
                'playweek': event.playweek,
                'name': event.name,
                'start_time': event.start_time,
                'costing': {
                    'take': take,
                    'bor_cost': bor_cost,
                    'refunded': refunded,
                },
                'showings': [s.id for s in event.showings.all()]
            }
            event_dicts.append(event_dict)

            if len(event.showings.all()) == 0:
                continue

            this_costing = dict(event_dict['costing'])
            this_costing['take'] = this_costing['take'] / len(event.showings.all())

            for showing in event.showings.all():
                showing_dict = showings.setdefault(showing.id, {
                    'playweek': event.playweek,
                    'name': showing.film.name,
                    'film_id': showing.film_id,
                    'start_time': showing.start_time,
                    'costing': {
                        'take': Decimal(0), 'bor_cost': Decimal(0), 'refunded': Decimal(0)
                    },
                    'royalties_percent': showing.film.royalties_percent,
                    'royalties_minimum': showing.film.royalties_minimum,
                    'royalties_troytastic': 1.2 if showing.film.royalties_troytastic else 1.0
                })
                for k, v in this_costing.items():
                    showing_dict['costing'][k] += v
 
        return {
            'events': event_dicts,
            'showings': showings
        }

    def get_data(self, raw_data):

        playweek_showings = {}
        # we need to group into playweek-film
        for showing in raw_data['showings'].values():
            playweek_showings.setdefault('{}***{}'.format(showing['playweek'], showing['name']), []).append(showing)

        # now we flatten it into output data
        out_data = []
        for showings in sorted(playweek_showings.values(), key=lambda x: x[0]['playweek']):
            playweek = showings[0]['playweek']
            name = showings[0]['name']
            previous_playweek = playweek - datetime.timedelta(days=7)
            has_previous_playweek = '{}***{}'.format(previous_playweek, name) in playweek_showings.keys()
            if showings[0]['royalties_minimum'] is not None:
                guarantee = Decimal(showings[0]['royalties_minimum']) if not has_previous_playweek else Decimal(0)
            else:
                guarantee = None
            out_data.append({
                'headings': [playweek.strftime('%Y %m %d'), name, 0, 0, 0, 0],
                'data': []
            })
            d = out_data[-1]['data']
            h = out_data[-1]['headings']
            running_totals = {'take': Decimal(0), 'bor_cost': Decimal(0), 'refunded': Decimal(0)}
            for showing in showings:
                d.append([
                    showing['start_time'].strftime('%Y %m %d'),
                    '',
                    quantize(showing['costing']['take']),
                    quantize(showing['costing']['refunded']),
                    '',
                    ''
                ])
                for k, v in showing['costing'].iteritems():
                    running_totals[k] += v
            h[2] = quantize(running_totals['take'])
            h[3] = quantize(running_totals['refunded'])
            if showings[0]['royalties_percent'] is not None and guarantee is not None:
                bor_cost_novat = quantize(running_totals['bor_cost'] / Decimal(1.2), rounding=decimal.ROUND_DOWN)
                rental_cost_novat = quantize(max(bor_cost_novat * Decimal(showings[0]['royalties_percent']) / 100, guarantee))
                rental_cost_novat = (max(0, rental_cost_novat - guarantee) * Decimal(showings[0]['royalties_troytastic'])) + guarantee
                rental_cost = rental_cost_novat * Decimal(1.2)
                h[4] = quantize(rental_cost_novat)
                h[5] = quantize(((running_totals['take'] - running_totals['refunded']) / Decimal(1.2)) - h[4])
            else:
                h[4] = 0
                h[5] = 0
        return out_data

    def get_foot(self, raw_data, data):
        foot = ['', '', Decimal(0), Decimal(0), Decimal(0), Decimal(0)]
        for group in data:
            n = 2
            for v in group['headings'][2:]:
                foot[n] += v
                n += 1
        for x in range(len(foot)):
            if foot[x] != '':
                foot[x] = foot[x].quantize(Decimal('.01'))
        return foot
