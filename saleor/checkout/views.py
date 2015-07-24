from django.http.response import Http404
from django.shortcuts import redirect

from . import Checkout
from ..cart.utils import has_available_products


def details(request, step):
    if not request.cart or not has_available_products(request.cart):
        return redirect('cart:index')
    checkout = Checkout(request)
    if not step:
        return redirect(checkout.get_next_step())
    try:
        step = checkout[step]
    except KeyError:
        raise Http404()
    response = step.process(extra_context={'checkout': checkout})
    if not response:
        checkout.save()
        return redirect(checkout.get_next_step())
    return response
