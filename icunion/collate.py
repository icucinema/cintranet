from . import eactivities, public

def collate_product_info(eactivities, public):
    products = {}
    for eactivities_product in eactivities:
        products[eactivities_product['name']] = eactivities_product
    for public_product in public:
        p = products[public_product.get_name()]
        p['org_id'] = public_product.id
        p['remaining_count'] = public_product.get_remaining()
        if p['remaining_count'] is not None:
            p['total_count'] = p['remaining_count'] + p['purchased_count']
        else:
            p['total_count'] = None
        pp_skus = public_product.get_skus()
        if pp_skus:
            for pp_sku in pp_skus:
                this_sku = None
                for ea_sku in p['skus']:
                    if ea_sku['name'] == pp_sku.name:
                        this_sku = ea_sku
                        break
                else:
                    continue
                ea_sku['org_id'] = this_sku.id
                ea_sku['remaining_count'] = this_sku.get_remaining()
                if ea_sku['remaining_count'] is not None:
                    ea_sku['total_count'] = ea_sku['remaining_count'] + ea_sku['purchased_count']
                else:
                    ea_sku['total_count'] = None 
        elif len(p['skus']) == 1:
            s = p['skus'][0]
            s['remaining_count'] = p['remaining_count']
            s['total_count'] = p['total_count']
    return products

def get_product_info(eac, public_url, club_id):
    public_products = public.ProductList(public_url).get_products()
    eactivities_products = eac.fetch_available_products(club_id)
    return collate_product_info(eactivities_products, public_products)

if __name__ == '__main__':
    import sys
    from pprint import pprint
    pprint(get_product_info(eactivities.EActivities(sys.argv[1]), "https://www.imperialcollegeunion.org/shop/club-society-project-products/cinema-products/", 411))
