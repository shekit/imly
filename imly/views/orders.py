from datetime import date, timedelta
from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from plata.shop.models import Order, OrderItem
from django.db.models import Sum
from imly.models import StoreOrder 
from django.views.decorators.csrf import csrf_exempt

class UserOrders(ListView):
    model = Order
    template_name = 'imly_user_orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, confirmed__gte=date.today()).order_by('confirmed')

class UserOrder(DetailView):
    model = Order
    template_name = 'imly_user_order.html'

class StoreOrders(ListView):
    model = StoreOrder
    template_name = 'imly_store_orders.html'

    def get_queryset(self):
        self.store =  self.request.user.store
        return self.store.storeorder_set.filter(order__status = Order.IMLY_CONFIRMED)

        

    def get_context_data(self, **kwargs):
        context = super(StoreOrders, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        context['today'] = [order for order in qs if (order.delivered_on.date() == date.today() and order.order.status == 60 )]
        context['tomorrow'] = [order for order in qs if (order.delivered_on.date()  == date.today() + timedelta(days=1) and order.order.status == 60)]
        # setting the store in order to call order store total in template
        '''for order in context['today'] + context['tomorrow']:
            order.store = self.request.user.store'''
        newer = [order for order in qs if (order.delivered_on.date() > date.today() + timedelta(days=1) and order.order.status == 60 )]
        dates = []
        context['newer'] = []
        for order in newer:
            #order.store = self.request.user.store # setting the store in order to call order store total in template
            delivery_date = order.delivered_on.date() 
            if delivery_date in dates:
                context['newer'][dates.index(delivery_date)][1].append(order)
            else:
                dates.append(delivery_date)
                context['newer'].append((delivery_date, [order]))
        return context

def update_store_orders_for_order(request, pk):
#    if request.method == 'POST':
        order = Order.objects.get(pk=pk)
        StoreOrder.update_for_order(order)
        return redirect('/shop/cart/')

def update_cart(request,pk):
    oi = OrderItem.objects.get(pk=pk)
    order = oi.order
    oi.delete()
    order.recalculate_total()
    return redirect('/shop/cart/')

@csrf_exempt
def update_quantity(request):
    oi_id = request.POST.getlist('order_item')[0]
    oi = OrderItem.objects.get(pk=oi_id)
    oi.quantity = oi.quantity + 1
    oi.save()
    return HttpResponse('Success')