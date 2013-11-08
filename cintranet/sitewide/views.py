from django.shortcuts import render
from django.views.generic import TemplateView

import icunion

ICU_PRODUCT_LIST_PAGE = "https://www.imperialcollegeunion.org/shop/club-society-project-products/cinema-products/"

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # we're looking for:
        # Membership count
        cinema_club = icunion.public.Club(411)

        products = icunion.public.ProductList(ICU_PRODUCT_LIST_PAGE).get_products()

        my_context = {
            'stats': [
                {
                    'link': 'https://www.imperialcollegeunion.org/activities/a-to-z/411',
                    'title': 'Members',
                    'value': cinema_club.get_members(),
                    'class': 'primary'
                }
            ]
        }

        for product in products:
            try:
                sold = product.get_sold()
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
                    'link': product.url,
                    'title': '{} sold'.format(product.name),
                    'value': sold,
                    'class': btn_class
                })
            except icunion.exceptions.UnionResponseException:
                pass

        if 'view' not in kwargs:
            kwargs['view'] = self
        kwargs.update(my_context)
        return kwargs