from django.views.generic import ListView, DetailView
from plata.shop.models import Order, OrderItem
from datetime import date, timedelta
from collections import OrderedDict
from django.db.models import Sum

class UserOrders(ListView):
    model = Order
    template_name = 'imly_user_orders.html'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user, confirmed__gte=date.today()).order_by('confirmed')

class UserOrder(DetailView):
    model = Order
    template_name = 'imly_user_order.html'

class StoreOrders(ListView):
    model = Order
    template_name = 'imly_store_orders.html'

    def get_queryset(self):
        store =  self.request.user.store
        orders = Order.objects.filter(items__product__in=store.product_set.all()).order_by('confirmed').distinct()
        return orders

    def get_context_data(self, **kwargs):
        context = super(StoreOrders, self).get_context_data(**kwargs)
        # simple approach to grouping, improve this later
        qs = self.get_queryset()
        context['today'] = [order for order in qs.all() if order.delivery_date.date() == date.today()]
        context['tomorrow'] = [order for order in qs.all() if order.delivery_date.date()  == date.today() + timedelta(days=1)]
        # setting the store in order to call order store total in template
        for order in context['today'] + context['tomorrow']:
            order.store = self.request.user.store
        newer = [order for order in qs.all() if order.delivery_date.date() > date.today() + timedelta(days=1)]
        dates = []
        context['newer'] = []
        for order in newer:
            order.store = self.request.user.store # setting the store in order to call order store total in template
            delivery_date = order.delivery_date.date() 
            if delivery_date in dates:
                context['newer'][dates.index(delivery_date)][1].append(order)
            else:
                dates.append(delivery_date)
                context['newer'].append((delivery_date, [order]))
        return context

class StoreOrder(DetailView):
    model = OrderItem
    template_name = 'imly_store_order.html'

    def get_queryset(self):
        pass