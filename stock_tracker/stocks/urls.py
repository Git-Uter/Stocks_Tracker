from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_stock, name="add_stock"),
    path("update/<int:stock_id>/", views.update_stock, name="update_stock"),
    path("delete/<int:stock_id>/", views.delete_stock, name="delete_stock"),
    path("sell/<int:stock_id>/", views.sell_stock, name="sell_stock"),
    path("sold/", views.sold_stocks, name="sold_stock"),
    path("bep_analysis", views.bep_analysis, name="bep_analysis"),
    path("download/", views.download_sold_stocks, name="download_sold_stocks"),
]
