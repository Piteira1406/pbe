from oscar.apps.dashboard.catalogue.views import ProductListView as CoreProductListView
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')

class ProductListView(CoreProductListView):
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_superuser:
            return qs
        try:
            return qs.filter(stockrecords__partner__user=user).distinct()
        except:
            return qs.none()
