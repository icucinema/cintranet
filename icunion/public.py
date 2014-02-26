import requests
from bs4 import BeautifulSoup

from .exceptions import *

UNION_STOCK_QUERY_URL = 'https://www.imperialcollegeunion.org/uc_out_of_stock/query'

class ProductList(object):
    def __init__(self, url):
        self.url = url
        self.products = None

    def get_products(self):
        if self.products is None:
            products = []

            # make the request
            r = requests.get(self.url)
            r.raise_for_status()

            # build the tree
            s = BeautifulSoup(r.text)

            # find all products
            product_divs = s.select(".view-uc-catalog .views-row")
            for product_div in product_divs:
                product_id = product_div.find("input", attrs={'type':"hidden", 'name':"nid"}).attrs['value']
                product_name = product_div.find("div", class_="views-field-title").a.get_text()
                products.append(Product(id=product_id, name=product_name))

            # reassign
            self.products = products
        return self.products


class Product(object):
    def __init__(self, id, name=None, initial=100, skus=None):
        self.id = id
        self.name = name
        self.initial = initial
        self.skus = skus

        self.remaining = None

    def get_name(self):
        if self.name is None:
            self.update_from_page()
        return self.name

    def get_skus(self):
        if self.skus is None:
            self.update_from_page()
        return self.skus

    def update_from_page(self):
        r = requests.get(self.url)
        r.raise_for_status()
        s = BeautifulSoup(r.text)
        self.name = s.find("h2").text

        sku_select = s.find("select")
        if sku_select:
            sku_attr_id = sku_select.attrs['id']
            sku_attr_id = sku_attr_id[sku_attr_id.rfind('-')+1:]

            self.skus = skus = []
            for sku_option in s.find("select").find_all("option"):
                skus.append(SKU(self, sku_attr_id, unicode(sku_option.attrs['value']), unicode(sku_option.text)))

        sku_radios = s.find("div", class_="form-type-radios")
        if sku_radios:
            sku_attr_id = sku_radios.attrs['class'][-1]
            sku_attr_id = sku_attr_id[sku_attr_id.rfind('-')+1:]

            self.skus = skus = []
            for sku_option in s.find("div", class_="form-type-radios").find_all("input", type="radio"):
                txt = unicode(sku_option.find_next_sibling("label").text)
                txt = txt[:txt.rfind(', ')]
                skus.append(SKU(self, sku_attr_id, unicode(sku_option.attrs['value']), txt))

    def get_remaining(self):
        if self.remaining is not None:
            return self.remaining

        # build the request body
        fid = 'uc-product-add-to-cart-form-{}'.format(self.id)
        body = {
            'form_ids[]': fid,
            'node_ids[]': self.id
        }

        # send the request
        r = requests.post(UNION_STOCK_QUERY_URL, data=body)
        r.raise_for_status()

        # parse the response
        try:
            rj = r.json()
            self.remaining = int(rj[fid]) if rj[fid] is not None else None
            return self.remaining
        except:
            raise UnionResponseException("Invalid response from ICU: {}".format(r.text))

    def get_sold(self):
        return self.initial - self.get_remaining()

    @property
    def url(self):
        return "https://www.imperialcollegeunion.org/node/{}".format(self.id)

class SKU(object):
    def __init__(self, product, attr_id, id, name, remaining=None):
        self.product = product
        self.attr_id = attr_id
        self.id = id
        self.name = name
        self.remaining = remaining

    def get_remaining(self):
        if self.remaining is not None:
            return self.remaining

        # build the request body
        fid = 'uc-product-add-to-cart-form-{}'.format(self.product.id)
        body = {
            'form_ids[]': fid,
            'node_ids[]': self.product.id,
            'attr_ids[]': '{}:{}:{}'.format(self.product.id, self.attr_id, self.id)
        }

        # send the request
        r = requests.post(UNION_STOCK_QUERY_URL, data=body)
        r.raise_for_status()

        # parse the response
        try:
            rj = r.json()
            self.remaining = int(rj[fid]) if rj[fid] is not None else None
            return self.remaining
        except:
            raise UnionResponseException("Invalid response from ICU: {}".format(r.text))


class Club(object):
    def __init__(self, id):
        self.id = id
        self.members = None

    @property
    def url(self):
        return "https://www.imperialcollegeunion.org/activities/a-to-z/{}".format(self.id)

    def get_members(self):
        if self.members is None:
            # make the request...
            r = requests.get(self.url)
            r.raise_for_status()

            # parse the HTML into a tree
            s = BeautifulSoup(r.text)
            self.members = int(s.select(".current-members b")[0].text)


        return self.members
