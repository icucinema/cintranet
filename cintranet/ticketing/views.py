import datetime
import decimal
import json
import pickle
from io import BytesIO

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.views.generic import TemplateView
from django.core.files import File
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.timezone import now

import dateutil.parser

from . import models, bor_generator

class IndexView(TemplateView):
    template_name = 'ticketing/index.html'

def angular_partial_view(request, partial):
    return HttpResponseRedirect(staticfiles_storage.url('ticketing/' + partial))

def generate_bor_information(request, film_id, show_week):
    film = get_object_or_404(models.Film, pk=film_id)
    start_date = datetime.datetime.strptime(show_week, "%Y-%m-%d")

    agg_data = bor_generator.build_agg_data_for_show_week(film, start_date)

    out_agg_data = {}
    # make it acceptable
    for showing_date, showing_tickets in agg_data.iteritems():
        out_agg_data[showing_date.isoformat()] = z = []
        for showing_ticket in showing_tickets:
            new_showing_ticket = {}
            for k, v in showing_ticket.iteritems():
                if isinstance(v, decimal.Decimal):
                    new_showing_ticket[k] = int(v * 100)
                else:
                    new_showing_ticket[k] = v
            z.append(new_showing_ticket)

    return HttpResponse(json.dumps(out_agg_data), content_type='application/json')

def generate_bor_draft_pdf(request, film_id, show_week):
    film = get_object_or_404(models.Film, pk=film_id)
    start_date = datetime.datetime.strptime(show_week, "%Y-%m-%d")
    show_week = bor_generator.get_show_week(start_date)
    show_week_str = show_week.strftime('%Y-%m-%d')

    try:
        bor = models.BoxOfficeReturn.objects.get(film=film, start_time=start_date)
        return HttpResponseRedirect(bor.pdf_file.url)
    except models.BoxOfficeReturn.DoesNotExist:
        pass

    jd = json.loads(request.POST['jsondata'])

    back_to_decimal = ['refund', 'price', 'take']

    constituted_data = {}
    for showing_date, showing_tickets in jd.iteritems():
        showing_date = dateutil.parser.parse(showing_date)
        constituted_data[showing_date] = z = []
        for showing_ticket in showing_tickets:
            new_showing_ticket = {}
            for k, v in showing_ticket.iteritems():
                if k.startswith('$'): continue
                if v is None:
                    v = 0
                if k in back_to_decimal:
                    new_showing_ticket[k] = decimal.Decimal(v) / 100
                else:
                    new_showing_ticket[k] = v
            z.append(new_showing_ticket)

    data_data = bor_generator.build_data_structures(constituted_data)
    iobuf = BytesIO()
    if request.GET.get('save', None) != 'true':
        watermark = "DRAFT"
    else:
        watermark = False

    bor_generator.generate_pdf(iobuf, film, show_week, request.user.get_full_name(), now(), data_data, watermark)


    if request.GET.get('save', None) == 'true':
        bor = models.BoxOfficeReturn(raw_data=request.POST['jsondata'], film=film, start_time=start_date)
        iobuf_djfile = File(iobuf)
        bor.pdf_file.save('BOR_{}-{}.pdf'.format(show_week_str, film.id), iobuf_djfile)  # FieldFile.save saves the model too

    pdf = iobuf.getvalue()
    iobuf.close()

    return HttpResponse(pdf, content_type='application/pdf')
