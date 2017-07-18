# -*- coding: utf-8 -*-
from cornice.service import Service, get_services
from openregistry.api.constants import VERSION


spore = Service(name='spore', path='/spore', renderer='json')

#####
# from cornice.ext.spore import generate_spore_description
import re

URL_PLACEHOLDER = re.compile(r'\{([a-zA-Z0-9_-]*)\}')


def generate_spore_description(services, name, base_url, version, **kwargs):
    """Utility to turn cornice web services into a SPORE-readable file.

    See https://github.com/SPORE/specifications for more information on SPORE.
    """
    URL_PLACEHOLDER = re.compile(r'\{([a-zA-Z0-9_-]*)\}')

    spore_doc = dict(
        base_url=base_url,
        name=name,
        version=version,
        expected_status=[200, ],
        methods={},
        **kwargs
    )

    for service in services:
        # the :foobar syntax should be removed.
        # see https://github.com/SPORE/specifications/issues/5
        service_path = URL_PLACEHOLDER.sub(':\g<1>', service.path)

        # get the list of placeholders
        service_params = URL_PLACEHOLDER.findall(service.path)

        for method, view, args in service.definitions:
            format_name = args['renderer']
            if 'json' in format_name:
                format_name = 'json'

            view_info = {
                'path': service_path,
                'method': method,
                'formats': [format_name]
            }
            if service_params:
                view_info['required_params'] = service_params

            if getattr(view, '__doc__'):
                view_info['description'] = view.__doc__

            # we have the values, but we need to merge this with
            # possible previous values for this method.
            method_name = '{method}_{service}'.format(
                method=method.lower(), service=service.name.lower())
            spore_doc['methods'][method_name] = view_info

    return spore_doc
####


@spore.get()
def get_spore(request):
    services = get_services()
    return generate_spore_description(services, 'Service name', request.application_url, VERSION)