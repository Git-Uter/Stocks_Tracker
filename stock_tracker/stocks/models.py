from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User  # Import User model
from datetime import date


class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to User model
    SCRIP = models.CharField(max_length=100)
    Purchased_Date = models.DateField(auto_now_add=True)
    Purchased_At = models.FloatField(default=0)
    Interest_Rate = models.FloatField(default=0)
    Quantity = models.IntegerField(default=0)
    WACC = models.FloatField(default=0)
    LTP = models.FloatField(default=0)
    Sold = models.BooleanField(default=False)
    Sellable = models.BooleanField(default=True)
    Sold_At = models.FloatField(default=0)
    Sold_Date = models.DateField(null=True, blank=True)
    Broker_Commission = models.FloatField(default=0)

    def clean(self):
        if self.Purchased_At < 0:
            raise ValidationError({"Purchased_At": "Cannot be negative"})
        if self.Quantity < 0:
            raise ValidationError({"Quantity": "Cannot be negative"})
        if self.LTP < 0:
            raise ValidationError({"LTP": "Cannot be negative"})
        if self.Broker_Commission < 0:
            raise ValidationError({"Broker_Commission": "Cannot be negative"})
        if self.Sold_At < 0:
            raise ValidationError({"Sold_At": "Cannot be negative"})
        if self.Interest_Rate < 0:
            raise ValidationError({"Interest_Rate": "Cannot be negative"})

    def save(self, *args, **kwargs):
        # Capitalize SCRIP
        self.SCRIP = self.SCRIP.upper()

        # Handle duplicates and calculate WACC only on creation
        if self.pk is None:  # Only execute on creation (not update)
            if self.WACC == 0:
                # Check for duplicates by SCRIP and user
                duplicates = Stock.objects.filter(
                    SCRIP=self.SCRIP, Sold=False, user=self.user
                )

                if duplicates.exists():
                    # Mark older duplicates as non-sellable
                    duplicates.update(Sellable=False)

                    # Remove rows with WACC > 0 (non-zero WACC)
                    duplicates.filter(WACC__gt=0).delete()

                    # Calculate new WACC
                    new_wacc = self.calculate_new_wacc(duplicates)

                    # Calculate weighted average interest rate
                    total_net_investment = (
                        sum(dup.net_investment() for dup in duplicates)
                        + self.net_investment()
                    )
                    total_weighted_interest = sum(
                        dup.Interest_Rate * dup.net_investment() for dup in duplicates
                    ) + (self.Interest_Rate * self.net_investment())

                    # If total net investment is greater than zero, calculate weighted interest rate
                    WHT_Interest_Rate = (
                        total_weighted_interest / total_net_investment
                        if total_net_investment > 0
                        else 0
                    )

                    # Create a new entry with updated WACC
                    Stock.objects.create(
                        user=self.user,  # Assign user
                        SCRIP=self.SCRIP,
                        Purchased_At=new_wacc,
                        Interest_Rate=WHT_Interest_Rate,
                        Quantity=sum(dup.Quantity for dup in duplicates)
                        + self.Quantity,
                        WACC=new_wacc,
                        LTP=self.LTP,
                        Sold=False,
                        Sellable=True,  # New entry will be sellable
                        Broker_Commission=self.Broker_Commission,
                    )

                    # Mark the current stock as non-sellable
                    self.Sellable = False

        super().save(*args, **kwargs)

    def calculate_new_wacc(self, duplicates):
        total_value = sum(dup.Quantity * dup.Purchased_At for dup in duplicates) + (
            self.Quantity * self.Purchased_At
        )
        total_quantity = sum(dup.Quantity for dup in duplicates) + self.Quantity
        if total_quantity == 0:
            return 0
        return total_value / total_quantity

    def matured_days(self):
        # Check if Sold_Date is not None, and return the correct days
        if self.Sold_Date:
            return (self.Sold_Date - self.Purchased_Date).days
        return (date.today() - self.Purchased_Date).days

    def net_investment(self):
        return (
            self.WACC * self.Quantity
            if self.WACC
            else self.Purchased_At * self.Quantity
        )

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
