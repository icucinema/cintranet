# -*- coding: utf-8 -*-

from decimal import Decimal, getcontext
import datetime
from . import models as m
from django.db.models import Count

# Proof of Concept code for generating Box Office Returns
# BORs are generated per Film per Play Week
# Play Weeks are Friday->Thursday, because cinema industry

def get_show_week(for_date):
    # go backwards until we find a Friday!
    show_week = for_date.date()
    # a Friday is weekday() 4
    one_day = datetime.timedelta(days=1)
    while show_week.weekday() != 4:
        show_week -= one_day 
    return show_week
def get_show_week_end(for_date):
    if for_date.weekday() != 4:
        for_date = get_show_week(for_date)
    return for_date + datetime.timedelta(days=7)

def format_money(money):
    # format a Decimal to a currency amount!
    return "£{}".format(money.quantize(Decimal('1.00')))

def determine_ticket_type(tt_name):
    if 'Non-members' in tt_name:
        return 'Adult'
    elif 'Members' in tt_name or tt_name == 'Season':
        return 'Concession'
    return 'Adult'

def make_agg_data_key(ticket_type, bor_price):
    return "{}@{}".format(ticket_type, bor_price.quantize(Decimal('1.00')))

def update_showing_agg_data(showing_agg_data, tt_name, bor_price, update_vals):
    ticket_type = determine_ticket_type(tt_name)
    sad = showing_agg_data.setdefault(make_agg_data_key(ticket_type, bor_price), {
        'price': bor_price, 'ticket_type': ticket_type,
        'sold_tickets': 0, 'take': Decimal(0),
        'refund_count': 0, 'refund': Decimal(0),        
    })
    for k, v in update_vals.iteritems():
        sad[k] += v
    return sad



def build_agg_data_for_show_week(film, show_week):
    show_week = get_show_week(show_week)

    showings = film.showing_weeks.get(start_time=show_week).showings.all()

    agg_data = {}
    
    for showing in showings:
        showing_agg_data = {}
    
        ticket_counts = showing.tickets().exclude(status='void').values('ticket_type__id', 'ticket_type__name', 'ticket_type__box_office_return_price').annotate(count=Count('id'))
        refunded_ticket_counts = showing.tickets().filter(status='refunded').values('ticket_type__id', 'ticket_type__name', 'ticket_type__box_office_return_price').annotate(count=Count('id'))
    
        for ticket_type_count in ticket_counts:
            bor_price = ticket_type_count['ticket_type__box_office_return_price']
            tt_name = ticket_type_count['ticket_type__name']
            sold_count = ticket_type_count['count']

            bor_price /= m.TicketType.objects.get(pk=ticket_type_count['ticket_type__id']).event.showings.all().count()
    
            this_take = bor_price * sold_count
    
            update_showing_agg_data(showing_agg_data, tt_name, bor_price, {
                'sold_tickets': sold_count,
                'take': this_take
            })
    
        for ticket_type_count in refunded_ticket_counts:
            bor_price = ticket_type_count['ticket_type__box_office_return_price']
            tt_name = ticket_type_count['ticket_type__name']
            refunded_count = ticket_type_count['count']
    
            this_refunded = bor_price * refunded_count
            this_refunded /= m.TicketType.objects.get(pk=ticket_type_count['ticket_type__id']).event.showings.all().count()
    
            update_showing_agg_data(showing_agg_data, tt_name, bor_price, {
                'refund_count': refunded_count,
                'refund': this_refunded
            })
    
        agg_data[showing.start_time] = showing_agg_data.values()
    return agg_data

def calculate_showing_breakdown(tickettype_brkdns):
    current_data = {
        'take': Decimal(0), 'sold_tickets': 0, 'refund': Decimal(0), 'refund_count': 0
    }
    tickettype_breakdown = {}

    # now we have a dictionary mapping our internal tickettype key to a dictionary, so
    for breakdown in tickettype_brkdns:
        breakdown['ticket_type'] = '{} {}'.format(breakdown['ticket_type'], format_money(breakdown['price']))
        for k, v in breakdown.items():
            if k not in current_data.keys(): continue
            current_data[k] += v
    current_data['breakdown'] = sorted(tickettype_brkdns, key=lambda x: x['price'], reverse=True)
    return current_data
    

def build_data_structures(showing_brkdns):
    showing_breakdown = {}
    current_data = {
        'take': Decimal(0), 'sold_tickets': 0, 'refund': Decimal(0), 'refund_count': 0
    }
    for showing_start_time, breakdown in showing_brkdns.iteritems():
        showing_breakdown[showing_start_time] = ce = calculate_showing_breakdown(breakdown)
        for k, v in ce.items():
            if k not in current_data.keys(): continue
            current_data[k] += v
    current_data['breakdown'] = showing_breakdown
    return current_data


def generate_pdf(output_to, film, show_week, completer, completed_on, final_agg_data, with_watermark):
    # generate the pdf
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate
    from reportlab.lib.units import mm
    from reportlab.platypus.flowables import PageBreak, Spacer
    from reportlab.platypus.paragraph import Paragraph
    from reportlab.platypus.tables import colors, Table
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    
    stylesheet = getSampleStyleSheet()
    stylesheet['BodyText'].fontName = 'Times-Roman'
    MARGIN_SIZE = 25 * mm
    PAGE_SIZE = A4
    
    def create_pdfdoc(pdfdoc, story, with_watermark):
        def generate_watermark(canvas, doc):
            if not with_watermark: return
            canvas.saveState()
            canvas.setFont("Courier", 60)
            canvas.translate(700, 50)
            canvas.setFillGray(0.8, 0.5)
            canvas.rotate(45)
            for z in range(0, 1200, 60):
                canvas.drawCentredString(0, z, with_watermark)
            canvas.restoreState()
        pdf_doc = BaseDocTemplate(pdfdoc, pagesize=PAGE_SIZE, leftMargin=MARGIN_SIZE, topMargin=MARGIN_SIZE, rightMargin=MARGIN_SIZE, bottomMargin=MARGIN_SIZE)
        main_frame = Frame(MARGIN_SIZE, MARGIN_SIZE, PAGE_SIZE[0] - 2 * MARGIN_SIZE, PAGE_SIZE[1] - 2 * MARGIN_SIZE, leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='mainframe')
        main_template = PageTemplate(id='maintemplate', frames=[main_frame], onPage=generate_watermark)
        pdf_doc.addPageTemplates([main_template])
        pdf_doc.build(story)
    
    
    # yay, stack overflow: http://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
    def suffix(d):
        return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')
    def custom_strftime(format, t):
        return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))
    
    def b(text):
        if isinstance(text, Paragraph):
            text = text.text
        return Paragraph("<b>{}</b>".format(text), stylesheet['BodyText'])
    def i(text):
        if isinstance(text, Paragraph):
            text = text.text
        return Paragraph("<i>{}</i>".format(text), stylesheet['BodyText'])
    
    TABLE_STYLE_FIRST_COLUMN_BOLDED = [
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold')
    ]
    
    def generate_details_table(film, show_week, total_tickets, total_take, total_refunded):
        table_style = list(TABLE_STYLE_FIRST_COLUMN_BOLDED) + [
        ]
    
        table_rows = [
            ['Film Title:', film.name],
            ['Certificate:', film.certificate],
            ['', ''], # padding!
            ['Show Week Beginning:', custom_strftime("%A {S} %B", show_week)],
            ['Attendance:', total_tickets],
            ['Gross Take:', format_money(total_take)],
            ['Refunded:', format_money(total_refunded)]
        ]
    
        return Table(table_rows, style=table_style, hAlign='LEFT')
    
    def generate_breakdown_table(agg_data):
        table_style = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('LEFTPADDING', (0,0), (-1,-1), 3),
            ('RIGHTPADDING', (0,0), (-1,-1), 3),
            ('FONTNAME', (0,0), (-1,-1), 'Times-Bold'),
            ('FONTNAME', (0,1), (-1,-1), 'Times-Roman'),
            ('FONTSIZE', (0,0), (-1,-1), 10)
        ]
        
        table_rows = [['', 'Tickets', 'Gross Take', 'Refunded']]
        for start_time, data in agg_data.iteritems():
            rows = [[i(x) for x in [b(custom_strftime("%A {S} %B @ %H:%M", start_time)), data['sold_tickets'], format_money(data['take']), format_money(data['refund'])]]]
            for tt_data in data['breakdown']:
                rows.append([" - " + tt_data['ticket_type'], tt_data['sold_tickets'], format_money(tt_data['take']), format_money(tt_data['refund'])])
            table_rows.extend(rows)
        
        return Table(table_rows, style=table_style, colWidths=('43%', '19%', '19%', '19%'), hAlign='LEFT')
    
    def generate_footer_table():
        table_style = list(TABLE_STYLE_FIRST_COLUMN_BOLDED) + [
        ]
    
        table_rows = [
            ['Terms:', 'As agreed']
        ]
    
        return Table(table_rows, style=table_style, hAlign='LEFT')
    
    def generate_completion_table(completer, completed_on):
        table_style = list(TABLE_STYLE_FIRST_COLUMN_BOLDED) + [
            ('FONTSIZE', (0, 0), (-1,-1), 18)
        ]
    
        table_rows = [
            ['Completed By:', completer],
            ['Date:', completed_on.strftime('%d/%m/%Y')]
        ]
    
        return Table(table_rows, style=table_style, hAlign='LEFT', rowHeights=[23] * len(table_rows))
    
    story = []
    story.append(Paragraph('ICU Cinema - Box Office Return', stylesheet['Heading1']))
    story.append(Spacer(0, 10 * mm))
    story.append(generate_details_table(film, show_week, final_agg_data['sold_tickets'], final_agg_data['take'], final_agg_data['refund']))
    story.append(Spacer(0, 10 * mm))
    story.append(generate_breakdown_table(final_agg_data['breakdown']))
    story.append(Spacer(0, 10 * mm))
    story.append(generate_footer_table())
    story.append(Spacer(0, 3 * mm))
    story.append(Paragraph('I certify that these records accurately describe the admissions for the above mentioned film.', stylesheet['BodyText']))
    story.append(Spacer(0, 3 * mm))
    story.append(generate_completion_table(completer, completed_on))
    story.append(Spacer(0, 6 * mm))
    story.append(Paragraph("""<b>Imperial College Union Cinema</b>
    Imperial College Union
    Beit Quad
    Prince Consort Road
    London
    SW7 2BB
    
    <b>Email: cinema@imperial.ac.uk</b>""".replace("\n","<br />"), stylesheet['BodyText']))
    
    create_pdfdoc(output_to, story, with_watermark)

if __name__ == '__main__':
    film = m.Film.objects.get(name='Test Film A')
    show_week = get_show_week(film.showings.last().start_time)

    from io import BytesIO

    buff = BytesIO()

    completer = 'Luke Granger-Brown'
    completed_on = datetime.date.today()

    agg_data = build_agg_data_for_show_week(film, film.showings.last().start_time)
    print agg_data
    overview_data = build_data_structures(agg_data)
    generate_pdf(buff, film, show_week, completer, completed_on, overview_data, "DRAFT") 

    pdf = buff.getvalue()
    buff.close()
    with open('test.pdf', 'wb') as f:
        f.write(pdf)
