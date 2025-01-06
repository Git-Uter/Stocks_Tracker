from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User  # Import User model
from datetime import date


class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    SCRIP = models.CharField(max_length=100)
    WACC = models.FloatField(default=0)
    Purchased_Date = models.DateField(auto_now_add=True)
    Interest_Rate = models.FloatField(default=0)
    Quantity = models.IntegerField(default=0)
    LTP = models.FloatField(default=0)
    Sold = models.BooleanField(default=False)
    Sellable = models.BooleanField(default=True)
    Sold_At = models.FloatField(null=True, blank=True)
    Sold_Date = models.DateField(null=True, blank=True)
    Broker_Commission = models.FloatField(default=10)

    def clean(self):
        if self.WACC < 0:
            raise ValidationError({"Purchased_At": "Cannot be negative"})
        if self.Quantity < 0:
            raise ValidationError({"Quantity": "Cannot be negative"})
        if self.LTP < 0:
            raise ValidationError({"LTP": "Cannot be negative"})
        if self.Broker_Commission < 0:
            raise ValidationError({"Broker_Commission": "Cannot be negative"})
        if self.Sold_At is not None and self.Sold_At < 0:
            raise ValidationError({"Sold_At": "Sold_At cannot be negative."})
        if self.Interest_Rate < 0:
            raise ValidationError({"Interest_Rate": "Cannot be negative"})

    def matured_days(self):
        # Check if Sold_Date is not None, and return the correct days
        if self.Sold_Date:
            return (self.Sold_Date - self.Purchased_Date).days
        return (date.today() - self.Purchased_Date).days

    def net_investment(self):
        return self.WACC * self.Quantity

    def interest(self):
        current_interest = (
            (self.Interest_Rate / 100)
            * self.net_investment()
            * self.matured_days()
            / 365
        )
        return current_interest

    def current_value(self):
        return self.LTP * self.Quantity

    def current_pl(self):
        return self.current_value() - self.net_investment() - self.interest()

    def sold_value(self):
        return self.Sold_At * self.Quantity if self.Sold_At else 0

    def profit_booked(self):
        return max(0, self.sold_value() - self.net_investment() - self.interest())

    def loss_beared(self):
        return max(0, self.net_investment() + self.interest() - self.sold_value())

    def dp(self):
        return 25

    def pg_tax(self):
        profit = self.profit_booked()
        if self.matured_days() < 365:
            return profit * 0.07
        return profit * 0.03

    def net_profit(self):
        return max(
            0, self.profit_booked() - self.dp() - self.pg_tax() - self.Broker_Commission
        )

    def net_loss(self):
        if self.net_profit() > 0:
            return 0
        else:
            return self.loss_beared() + self.dp() + self.Broker_Commission

    def __str__(self):
        return self.SCRIP
