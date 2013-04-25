from django.views.generic import ListView, DetailView
from plata.shop.models import Order, OrderItem
from datetime import date, timedelta

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
        items = OrderItem.objects.filter(product__in=store.product_set.all())
        self.pending = self.request.GET.get('display', '') == 'pending'
        if self.pending:
            items = items.filter(order__confirmed__gte=date.today())
            items.order_by('order__confirmed')
        else:
            items = items.filter(order__confirmed__lte=date.today())
            items.order_by('-order__confirmed')
        return items

    def get_context_data(self, **kwargs):
        context = super(StoreOrders, self).get_context_data(**kwargs)
        # simple approach to grouping, improve this later
        context['pending'] = self.pending
        qs = self.get_queryset()
        context['today'] = [item for item in qs.all() if item.order.confirmed.date() == date.today()]
        if self.pending:
            context['tomorrow'] = [item for item in qs.all() if item.order.confirmed.date() == date.today() + timedelta(days=1)]
            context['newer'] = [item for item in qs.all() if item.order.confirmed.date() > date.today() + timedelta(days=1)]
        else:
            context['yesterday'] = [item for item in qs.all() if item.order.confirmed.date() == date.today() + timedelta(days=-1)]
            context['older'] = [item for item in qs.all() if item.order.confirmed.date() < date.today() + timedelta(days=-1)]
        return context

class StoreOrder(DetailView):
    model = OrderItem
    template_name = 'imly_store_order.html'

    def get_queryset(self):
        pass