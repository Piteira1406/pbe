from oscar.apps.dashboard.orders.views import OrderListView as CoreOrderListView
from oscar.core.loading import get_model

Line = get_model('order', 'Line')

class OrderListView(CoreOrderListView):
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        try:
            return qs.filter(lines__partner__user=user).distinct()
        except:
            return qs.none()
