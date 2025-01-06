from django import forms
from .models import Stock


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            "SCRIP",
            "Purchased_Date",
            "WACC",
            "Quantity",
            "Interest_Rate",
        ]  # Add Purchased_Date here

    WACC = forms.FloatField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Price Per Share"}),
    )
    Interest_Rate = forms.FloatField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Interest Rate"}),
    )
    Quantity = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Number of Share Bought"}),
    )
    Purchased_Date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={"placeholder": "Enter Purchase Date", "type": "date"}
        ),  # type="date" for date picker
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["WACC"].label = "Purchased At"  # Change label for WACC
        self.fields["SCRIP"].widget.attrs.update({"placeholder": "Enter Stock Symbol"})
        # Set up default today's date (optional), but can be overwritten in the frontend
        self.fields["Purchased_Date"].initial = forms.DateField().widget.format_value(
            forms.DateField().prepare_value(None)
        )  # Set initial to today's date


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["SCRIP", "WACC", "Quantity", "LTP"]

    # Making fields read-only (use 'readonly' if data should still be submitted)
    SCRIP = forms.CharField(
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    WACC = forms.FloatField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={"readonly": "readonly"}),
    )
    Quantity = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={"readonly": "readonly"}),
    )
    LTP = forms.FloatField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(
            attrs={"placeholder": "Enter Latest Trading Price (LTP)"}
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["SCRIP"].widget.attrs.update({"readonly": "readonly"})
        self.fields["WACC"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Quantity"].widget.attrs.update({"readonly": "readonly"})
        self.fields["LTP"].widget.attrs.update(
            {"placeholder": "Enter Latest Trading Price (LTP)"}
        )


class StockSellForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            "SCRIP",
            "WACC",
            "Quantity",
            "LTP",
            "Sold_At",
            "Sold_Date",
            "Broker_Commission",
        ]

    SCRIP = forms.CharField(
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    WACC = forms.FloatField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={"readonly": "readonly"}),
    )
    Quantity = forms.IntegerField(
        required=True,
        min_value=1,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Quantity to Sell"}),
    )
    LTP = forms.FloatField(
        required=True,
        widget=forms.NumberInput(attrs={"readonly": "readonly"}),
    )

    Sold_At = forms.DecimalField(
        required=True,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Sale Price Per Share"}),
    )
    Sold_Date = forms.DateField(
        required=True,
        widget=forms.DateInput(
            attrs={"placeholder": "Enter Sold Date", "type": "date"}
        ),  # type="date" for date picker
    )

    Broker_Commission = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Broker Commission"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["SCRIP"].widget.attrs.update({"readonly": "readonly"})
        self.fields["WACC"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Quantity"].widget.attrs.update(
            {"placeholder": "Enter Quantity to Sell"}
        )
        self.fields["LTP"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Sold_At"].widget.attrs.update(
            {"placeholder": "Enter Sale Price Per Share"}
        )
        self.fields["Broker_Commission"].widget.attrs.update(
            {"placeholder": "Enter Broker Commission"}
        )
        self.fields["Sold_Date"].initial = forms.DateField().widget.format_value(
            forms.DateField().prepare_value(None)
        )
