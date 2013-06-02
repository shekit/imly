from django.views.generic import ListView, DetailView
from plata.shop.models import Order, OrderItem
from datetime import date, timedelta
from django.db.models import Sum
from imly.models import StoreOrder

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

class StoreOrder(DetailView):
    model = OrderItem
    template_name = 'imly_store_order.html'

    def get_queryset(self):
        pass