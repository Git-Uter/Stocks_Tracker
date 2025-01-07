from django.urls import path
from . import views

urlpatterns = [
    path("", views.add_stock, name="add_stock"),
    path("update/<int:stock_id>/", views.update_stock, name="update_stock"),
    path("delete/<int:stock_id>/", views.delete_stock, name="delete_stock"),
    path("sell/<int:stock_id>/", views.sell_stock, name="sell_stock"),
    path("sold_stocks/", views.sold_stocks, name="sold_stock"),
    path("bep_analysis", views.bep_analysis, name="bep_analysis"),
    path("financial_summary", views.financial_summary, name="financial_summary"),
    path(
        "download/sold_stocks", views.download_sold_stocks, name="download_sold_stocks"
    ),
    path("download/stocks_bep", views.download_stocks_bep, name="download_stocks_bep"),
]
