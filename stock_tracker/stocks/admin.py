from django.contrib import admin
from .models import Stock


class StockAdmin(admin.ModelAdmin):
    list_display = (
        "SCRIP",
        "Purchased_Date",
        "WACC",
        "matured_days",
        "Quantity",
        "net_investment",
        "LTP",
        "current_value",
        "current_pl",
        "Sold",
        "Sellable",
        "Sold_At",
        "sold_value",
        "Sold_Date",
        "profit_booked",
        "loss_beared",
        "dp",
        "pg_tax",
        "Broker_Commission",
        "net_profit",
        "net_loss",
    )

    # Add the calculated methods as properties to the admin
    def matured_days(self, obj):
        return obj.matured_days()

    matured_days.short_description = "Matured Days"

    def net_investment(self, obj):
        return obj.net_investment()

    net_investment.short_description = "Net Investment"

    def current_value(self, obj):
        return obj.current_value()

    current_value.short_description = "Current Value"

    def current_pl(self, obj):
        return obj.current_pl()

    current_pl.short_description = "Current P/L"

    def sold_value(self, obj):
        return obj.sold_value()

    sold_value.short_description = "Sold Value"

    def profit_booked(self, obj):
        return obj.profit_booked()

    profit_booked.short_description = "Profit Booked"

    def loss_beared(self, obj):
        return obj.loss_beared()

    loss_beared.short_description = "Loss Beared"

    def dp(self, obj):
        return obj.dp()

    dp.short_description = "DP"

    def pg_tax(self, obj):
        return obj.pg_tax()

    pg_tax.short_description = "PG Tax"

    def net_profit(self, obj):
        return obj.net_profit()

    net_profit.short_description = "Net Profit"

    def net_loss(self, obj):
        return obj.net_loss()

    net_loss.short_description = "Net Loss"


admin.site.register(Stock, StockAdmin)
