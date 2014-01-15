from django.shortcuts import render
from django.views.generic import TemplateView

import cott.models

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # we're looking for:
        # Membership count
        cm = cott.models.Product.objects.filter(currently_available=True)

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


            my_context['stats'].append({
                'link': 'javascript:;',
                'title': '{} sold'.format(product.name),
                'value': sold,
                'class': btn_class
            })

        if 'view' not in kwargs:
            kwargs['view'] = self
        kwargs.update(my_context)
        return kwargs
