# vim: set fileencoding=utf-8 :

import datetime
import decimal
import json
import collections
import random
import requests
Decimal = decimal.Decimal

from django.views.generic.base import TemplateView, View
from django.http import HttpResponse
from django.db.models import Count, Sum
from django.utils.timezone import now
from django.db import connection

from ticketing import models
from . import models as smodels

def get_default_date_bounds():
    my_now = now()
    start_at = my_now.replace(month=8, day=1, year=my_now.year if my_now.month >= 8 else my_now.year - 1)
    end_at = my_now
    return start_at, end_at

def quantize(d, **kwargs):
    return d.quantize(Decimal('.01'), **kwargs)

def flatten(d):
    return int(quantize(d) * 100)

class IndexView(TemplateView):
    template_name = 'stats/index.html'

class ReportView(TemplateView):
    template_name = 'stats/report.html'

    title = ''
    grouped = False
    data = []
    head = False
    foot = False
    col_classes = None

    def get_date_bounds(self):
        start_at, end_at = get_default_date_bounds()

        start_at_str = self.request.GET.get('start_at')
        end_at_str = self.request.GET.get('end_at')
        if start_at_str:
            start_at = datetime.datetime.strptime(start_at_str, '%Y-%m-%d')
        if end_at_str:
            end_at = datetime.datetime.strptime(end_at_str, '%Y-%m-%d')

        return start_at, end_at

    def get_head(self, raw_data, data):
        return self.head

    def get_foot(self, raw_data, data):
        return self.foot

    def get_data(self, raw_data):
        return self.data

    def get_col_classes(self, raw_data, data):
        if self.col_classes is None:
            return [None] * len(data)
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
        data['start_at'], data['end_at'] = self.get_date_bounds()
        data.update(super(ReportView, self).get_context_data(**kwargs))
        return data

class OverviewAudiencePlayweekView(ReportView):
    title = 'Audience Overview by Playweek'
    grouped = True
    data = []
    head = ['Film', 'Tickets Sold', 'Total Audience']

    def get_queryset(self):
        start_at, end_at = self.get_date_bounds()
        return models.Event.objects.all().extra({"pplayweek": "date_trunc('week', start_time - '4 days'::interval) + '4 days'::interval"}).order_by('pplayweek').filter(start_time__gt=start_at, start_time__lte=end_at).prefetch_related('showings', 'showings__week', 'showings__week__film')

    def get_raw_data(self):
        events = self.get_queryset()
        ticket_counts = dict(models.Ticket.objects.filter(status='live', ticket_type__event__in=[e.id for e in events]).values('ticket_type__event__id').annotate(count=Count('ticket_type__event__id')).order_by().values_list('ticket_type__event_id', 'count'))

        data = []

        for event in events:
            my_turnout = ticket_counts.get(event.id, 0) + event.additional_audience
            my_data = {
                'turnout': my_turnout,
                'playweek': event.pplayweek,
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
                turnout,
                turnout,
            ])

        adjustment = -(current_playweek_data['audience'] - current_playweek_data['turnout'])
        if adjustment != 0:
            cpd.append([
                '<Multi-Film Ticket Adjustment>',
                adjustment,
                ''
            ])

        return {
            'headings': [current_playweek.strftime('%b. %d %Y'), current_playweek_data['turnout'], current_playweek_data['audience']],
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
                current_playweek_data = {'turnout': 0, 'audience': 0, 'data': {}}
            current_playweek_data['turnout'] += raw_datum['turnout']
            current_playweek_data['audience'] += raw_datum['turnout'] * len(raw_datum['showings'])
            for showing in raw_datum['showings']:
                current_playweek_data['data'][showing['name']] = raw_datum['turnout'] + current_playweek_data['data'].get(showing['name'], 0)
        if current_playweek_data is not None:
            playweeks_data.append(self.process_raw_playweek(current_playweek, current_playweek_data))
        return playweeks_data

    def get_foot(self, raw_data, data):
        # sum everything
        x = ['{} playweeks'.format(len(data)), 0, 0]
        for d in data:
            x[1] += d['headings'][1]
            x[2] += d['headings'][2]
        return x

class OverviewAudienceFilmView(OverviewAudiencePlayweekView):
    grouped = False
    title = 'Audience Overview by Film'
    head = ['Film', 'Total Audience']

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
            total += raw_datum['turnout'] * len(raw_datum['showings'])
        return [None, total]

class OverviewMoneyView(ReportView):
    title = 'Money Overview'
    grouped = True 
    data = []
    head = ['Date', 'Film', 'Take (gross)', 'Refunded (gross)', 'Reported Take (net)', 'Paid (net)', 'Profit (net)']
    col_classes = ['col-date', None, None, None, None, None, None]

    def get_raw_data(self):
        start_at, end_at = self.get_date_bounds()
        events = models.Event.objects.all().order_by('start_time').filter(start_time__gt=start_at, start_time__lte=end_at).prefetch_related('showings', 'showings__week__film')

        event_dicts = []
        showings = {}

        cursor = connection.cursor()

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
            this_costing['bor_cost'] = this_costing['bor_cost'] / len(event.showings.all())

            for showing in event.showings.all():
                showing_dict = showings.setdefault(showing.id, {
                    'playweek': event.playweek,
                    'name': showing.film.name,
                    'film_id': showing.week.film_id,
                    'start_time': showing.start_time,
                    'costing': {
                        'take': Decimal(0), 'bor_cost': Decimal(0), 'refunded': Decimal(0)
                    },
                    'royalties_percent': showing.week.royalties_percent,
                    'royalties_minimum': showing.week.royalties_minimum,
                    'royalties_troytastic': 1.2 if showing.week.royalties_troytastic else 1.0
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
        for _, showings in sorted(playweek_showings.items(), key=lambda x: x[0] if len(x[1]) > 1 else '{}***{}'.format(x[1][0]['start_time'], x[1][0]['name'])):
            playweek = showings[0]['playweek']
            name = showings[0]['name']
            previous_playweek = playweek - datetime.timedelta(days=7)
            has_previous_playweek = '{}***{}'.format(previous_playweek, name) in playweek_showings.keys()
            if showings[0]['royalties_minimum'] is not None:
                guarantee = Decimal(showings[0]['royalties_minimum']) if not has_previous_playweek else Decimal(0)
            else:
                guarantee = None
            out_data.append({
                'headings': [playweek.strftime('%Y %m %d'), name, 0, 0, 0, 0, 0],
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
                    quantize(showing['costing']['bor_cost'] / Decimal(1.2), rounding=decimal.ROUND_DOWN),
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
                h[4] = quantize(bor_cost_novat)
                h[5] = quantize(rental_cost_novat)
                h[6] = quantize(((running_totals['take'] - running_totals['refunded']) / Decimal(1.2)) - h[5])
            else:
                h[4] = 0
                h[5] = 0
                h[6] = 0
        return out_data

    def get_foot(self, raw_data, data):
        foot = ['', '', Decimal(0), Decimal(0), Decimal(0), Decimal(0), Decimal(0)]
        for group in data:
            n = 2
            for v in group['headings'][2:]:
                foot[n] += v
                n += 1
        for x in range(len(foot)):
            if foot[x] != '':
                foot[x] = foot[x].quantize(Decimal('.01'))
        return foot

class DashboardJsonView(View):
    def get(self, request, *args, **kwargs):

        # try to work out if there are events today
        today = datetime.date.today()
        if request.GET.get('date', None) is not None:
            today = datetime.datetime.strptime(request.GET.get('date'), '%Y-%m-%d')
        tomorrow = today + datetime.timedelta(days=2)
        events = models.Showing.objects.filter(start_time__gte=today, start_time__lt=tomorrow)

        def format_punter(punter):
            if punter is None:
                return 'Guest'
            elif punter.name == '':
                return 'Unknown (ID: {})'.format(punter.id)
            return punter.name

        f_events = []
        event_event_ids = set()
        for e in events:
            tix = e.tickets().filter(status__in=('pending_collection', 'live')).select_related('ticket_type')

            take = Decimal('0')
            bor_cost = Decimal('0')
            for tick in tix:
                take += tick.ticket_type.sale_price / tick.ticket_type.event.showings.count()
                bor_cost += tick.ticket_type.box_office_return_price / tick.ticket_type.event.showings.count()

            minimum = Decimal(e.week.royalties_minimum or '0.00')
            percent = Decimal(e.week.royalties_percent or '0') / 100 + 1
            troytastic = 1.2 if e.week.royalties_troytastic else 1.0

            take_novat = quantize(take / Decimal(1.2), rounding=decimal.ROUND_DOWN)
            bor_cost_novat = quantize(bor_cost / Decimal(1.2), rounding=decimal.ROUND_DOWN)
            rental_cost_novat = quantize(max(bor_cost_novat * Decimal(percent) / 100, minimum))
            rental_cost_novat = (max(0, rental_cost_novat - minimum) * Decimal(troytastic)) + minimum

            other_showings = e.week.showings.exclude(id=e.id).filter(start_time__lt=e.start_time)
            prior_take = Decimal('0')
            for other_showing in other_showings:
                other_tix = other_showing.tickets().filter(status='live').select_related('ticket_type')
                for other_tick in other_tix:
                    prior_take += other_tick.ticket_type.sale_price / other_tick.ticket_type.event.showings.count()
            prior_take_novat = quantize(prior_take / Decimal(1.2), rounding=decimal.ROUND_DOWN)

            profit_novat = prior_take_novat + take_novat - rental_cost_novat
            tickets_to_breakeven = (-profit_novat) / (Decimal(3) / Decimal(1.2))

            f_event = {
                'name': e.name,
                'tickets': tix.count(),
                'take': flatten(take_novat),
                'reported_take': flatten(bor_cost_novat),
                'profit': flatten(profit_novat),
                'tickets_to_breakeven': int(tickets_to_breakeven.quantize(Decimal('1'), rounding=decimal.ROUND_UP))
            }
            
            f_events.append(f_event)

            for ev in e.events.all().values_list('id', flat=True):
                event_event_ids.add(ev)

            f_event['minimum'] = flatten(minimum)
            f_event['take_over_time'] = tot = collections.OrderedDict()
            for ticket in tix.order_by('timestamp'):
                x = ticket.timestamp.strftime('%Y-%m-%dT%H:%M:%S')
                tot[x] = tot.get(x, 0) + flatten(ticket.ticket_type.sale_price / Decimal(1.2))

        tickets_qs = models.Ticket.objects.filter(ticket_type__event__id__in=event_event_ids).select_related('ticket_type', 'ticket_type__event').order_by('-timestamp')

        today = {
            'events': f_events,
            'tickets': [{'id': t.id, 'name': format_punter(t.punter), 'type': t.ticket_type.name, 'cost': flatten(t.ticket_type.sale_price), 'event': t.ticket_type.event.name} for t in tickets_qs[:20]],
        }

        membership = {
            'this_year': smodels.StatsData.objects.get(key='membership_this_year').value,
            'last_year': self.change_year_to_this_year(smodels.StatsData.objects.get(key='membership_last_year').value)
        }

        products = []
        active_products = smodels.StatsData.objects.get(key='active_products').value
        for p in active_products:
            products.append({
                'name': p['name'],
                'sales': smodels.StatsData.objects.get(key='products_' + str(p['id'])).value
            })

        money = [y for (x, y) in smodels.StatsData.objects.get(key='finances').value['funding_overview'].iteritems() if x == 'SGI (1)']
        money = money[0] if money else 0

        ticker = self.generate_ticker()

        res = {
            'today': today,
            'membership': membership,
            'products': products,
            'money': money,
            'ticker': ticker,
            'live_data': self.generate_live_data()
        }
        return HttpResponse(json.dumps(res), content_type="application/json")

    def change_year_to_this_year(self, data):
        out = collections.OrderedDict()
        for k, v in data.iteritems():
            y, dash, rest = k.partition('-')
            y = str(int(y) + 1)
            new_k = y + dash + rest
            out[new_k] = v
        return out

    def generate_ticker(self):
        ticker = []

        now = datetime.datetime.now()
        this_monday = now.date() - datetime.timedelta(days=now.weekday())
        next_monday = this_monday + datetime.timedelta(days=7)
        last_monday = this_monday - datetime.timedelta(days=7)
        two_mondays_ago = last_monday - datetime.timedelta(days=7)
        last_september = datetime.date(now.year if now.month > 9 else now.year - 1, 9, 20)

        atmos_counter_start_date = datetime.datetime(2014, 9, 1)
        atmos_start_balance = 2059.33

        take_calc = lambda qs: qs.aggregate(take=Sum('ticket_type__sale_price'))['take'] or Decimal('0.00')
        tix = models.Ticket.objects.filter(status='live')
        take_last_week = take_calc(tix.filter(ticket_type__event__start_time__gte=last_monday, ticket_type__event__start_time__lt=this_monday)) or Decimal('0.00')
        take_this_week = take_calc(tix.filter(ticket_type__event__start_time__gte=this_monday, ticket_type__event__start_time__lt=next_monday)) or Decimal('0.00')
        tickets_sold_last_week = tix.filter(ticket_type__event__start_time__gte=last_monday, ticket_type__event__start_time__lt=this_monday).aggregate(n=Count('id'))['n'] or 0
        tickets_sold_this_week = tix.filter(ticket_type__event__start_time__gte=this_monday, ticket_type__event__start_time__lt=next_monday).aggregate(n=Count('id'))['n'] or 0
        tickets_sold_since_atmos_counter = tix.filter(ticket_type__event__start_time__gte=atmos_counter_start_date, ticket_type__event__start_time__lt=next_monday).aggregate(n=Count('id'))['n'] or 0

        lolz_feeling = random.choice([
            "So Nearly Done...",
            "So Close",
            "Nearly there",
            "Not far now",
            "Not quite",
            "#Phase2",
            "Just a little more",
            "Failing to acquire raked seating since 1993."
        ])

        ticker.append('​Current members: {}'.format(models.EntitlementDetail.objects.filter(entitlement__name='2014-15 Membership').count()))
        ticker.append('​Outstanding free tickets: {}'.format(models.EntitlementDetail.objects.filter(entitlement__name='2014-15 Members Free Ticket', remaining_uses__gte=1).count()))
        ticker.append('​Take last week: £{}'.format(take_last_week))
        ticker.append('​Take so far this week: £{}'.format(take_this_week))
        ticker.append('​Tickets to sell until we can afford Atmos: {}'.format(int((66919.56-atmos_start_balance)/2.18)-tickets_sold_since_atmos_counter))
        ticker.append('​Tickets sold last week: {}'.format(tickets_sold_last_week))
        if random.randint(1, 10) == 2:
            ticker.append('﻿#LivingTheDream')
        ticker.append('​Tickets sold this week: {}'.format(tickets_sold_this_week))
        ticker.append('​UCH Redevelopment Status Report: '+lolz_feeling)

        return ticker

    def grab_from(self, url):
        return "5"
        try:
            return requests.get(url).text
        except:
            return ""

    def generate_live_data(self):
        data = {}

        data['barco.temperature.ambient'] = self.grab_from('http://su-cinema.su.ic.ac.uk/info/barco.temperature.ambient.txt').strip()
        data['barco.runtime.bulb'] = self.grab_from('http://su-cinema.su.ic.ac.uk/info/barco.runtime.bulb.txt').strip()
        data['barco.runtime.bulb.max'] = self.grab_from('http://su-cinema.su.ic.ac.uk/info/barco.runtime.bulb.max.txt').strip()
        data['barco.runtime.bulb.warning'] = self.grab_from('http://su-cinema.su.ic.ac.uk/info/barco.runtime.bulb.warning.txt').strip()

        def safe_int(x):
            try:
                return int(x)
            except:
                return x
        data = dict((k, safe_int(v)) for (k, v) in data.items())

        return data

class DashboardView(TemplateView):
    template_name = 'stats/dashboard.html'
