from django import forms
from .models import Stock


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["SCRIP", "Purchased_At", "Quantity", "Interest_Rate"]

    Purchased_At = forms.FloatField(
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["SCRIP"].widget.attrs.update({"placeholder": "Enter Stock Symbol"})


class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = ["SCRIP", "Purchased_At", "Quantity", "LTP"]

    # Making fields read-only (use 'readonly' if data should still be submitted)
    SCRIP = forms.CharField(
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    Purchased_At = forms.FloatField(
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
        self.fields["Purchased_At"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Quantity"].widget.attrs.update({"readonly": "readonly"})
        self.fields["LTP"].widget.attrs.update(
            {"placeholder": "Enter Latest Trading Price (LTP)"}
        )


class StockSellForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [
            "SCRIP",
            "Purchased_At",
            "Quantity",
            "LTP",
            "Sold_At",
            "Broker_Commission",
        ]

    SCRIP = forms.CharField(
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )
    Purchased_At = forms.FloatField(
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
        widget=forms.NumberInput(attrs={"readonly": "readonly"}),
    )

    Sold_At = forms.DecimalField(
        required=True,
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={"placeholder": "Enter Sale Price Per Share"}),
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
        self.fields["Purchased_At"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Quantity"].widget.attrs.update({"readonly": "readonly"})
        self.fields["LTP"].widget.attrs.update({"readonly": "readonly"})
        self.fields["Sold_At"].widget.attrs.update(
            {"placeholder": "Enter Sale Price Per Share"}
        )
        self.fields["Broker_Commission"].widget.attrs.update(
            {"placeholder": "Enter Broker Commission"}
        )
