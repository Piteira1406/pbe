from django.apps import AppConfig
from oscar.apps.dashboard.catalogue.apps import CatalogueDashboardConfig
from oscar.apps.dashboard.orders.apps import OrdersDashboardConfig

class MarketplaceDashboardCatalogueConfig(CatalogueDashboardConfig):
    name = 'marketplace.dashboard.catalogue'
    label = 'marketplace_dashboard_catalogue'

class MarketplaceDashboardOrdersConfig(OrdersDashboardConfig):
    name = 'marketplace.dashboard.orders'
    label = 'marketplace_dashboard_orders'