from rest_framework import routers

from . import api_views, views

Route = routers.Route

class APIRouter(routers.DefaultRouter):
    routes = [
        # List route.
        Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='{basename}-list',
            initkwargs={'suffix': 'List'}
        ),
        # Detail route.
        Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated routes.
        # Generated using @action or @link decorators on methods of the viewset.
        Route(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{methodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
        Route(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            mapping={
                '{httpmethod}': '{toplevelmethodname}',
            },
            name='{basename}-{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_routes(self, viewset):
        ret = super(APIRouter, self).get_routes(viewset)

        toplevel_dynamic_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'toplevel_bind_to_methods', None)
            if httpmethods:
                httpmethods = [method.lower() for method in httpmethods]
                toplevel_dynamic_routes.append((httpmethods, methodname))
        
        extra_ret = []
        for route in self.routes:
            if route.mapping == {'{httpmethod}': '{toplevelmethodname}'}:
                for httpmethods, methodname in toplevel_dynamic_routes:
                    initkwargs = route.initkwargs.copy()
                    initkwargs.update(getattr(viewset, methodname).kwargs)
                    extra_ret.append(Route(
                        url=routers.replace_methodname(route.url, methodname),
                        mapping=dict((httpmethod, methodname) for httpmethod in httpmethods),
                        name=routers.replace_methodname(route.name, methodname),
                        initkwargs=initkwargs,
                    ))

        extra_ret.extend(ret)

        return extra_ret
