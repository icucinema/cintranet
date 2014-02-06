from django.shortcuts import render
from django.views.generic import TemplateView

import icusync.models

def get_button_class(sold, initial):
    btn_class = 'info'

    danger_max = initial * 0.2
    warning_max = initial * 0.4
    success_max = initial * 0.75

    if sold < danger_max:
        btn_class = 'danger'
    elif sold < warning_max:
        btn_class = 'warning'
    elif sold < success_max:
        btn_class = 'success'
        
    return btn_class
    

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # we're looking for:
        # Membership count
        cm = icusync.models.Product.objects.filter(currently_available=True)

        my_context = {
            'stats': [
                {
                    'link': 'https://www.imperialcollegeunion.org/activities/a-to-z/411',
                    'title': 'Members',
                    'value': cm.get(name__startswith='Cinema Membership ').sold,
                    'class': 'primary'
                }
            ]
        }
        cm = cm.exclude(name__startswith='Cinema Membership ')

        for product in cm:
            sold = product.sold
            initial = product.initial
            
            btn_class = get_button_class(sold, initial)

            my_context['stats'].append({
                'link': product.union_url,
                'title': '{} sold on shop'.format(product.name),
                'value': sold,
                'class': btn_class
            })
                
            sku_entitlements = icusync.models.SKUEntitlement.objects.filter(sku__product=product).select_related('entitlement')
            for sku_entitlement in sku_entitlements:
                my_context['stats'].append({
                    'link': product.union_url,
                    'title': '{} in DB'.format(sku_entitlement.entitlement.name),
                    'value': sku_entitlement.entitlement.entitlement_details.all().count(),
                    'class': 'default'
                })

        if 'view' not in kwargs:
            kwargs['view'] = self
        kwargs.update(my_context)
        return kwargs

class RemoteHeaderView(TemplateView):
    template_name = 'remoteheader.html'

    def get(self, *args, **kwargs):
        resp = super(RemoteHeaderView, self).get(*args, **kwargs)
        req = self.request
        origin = req.META.get('HTTP_ORIGIN', None)
        if origin is not None and origin.endswith('.icucinema.co.uk'):
            resp['Access-Control-Allow-Origin'] = origin
            resp['Access-Control-Allow-Credentials'] = 'true'
            resp['Access-Control-Allow-Methods'] = 'GET'
            resp['Access-Control-Max-Age'] = '600'
        return resp
