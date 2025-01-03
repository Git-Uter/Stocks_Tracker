from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Stock
from .forms import StockCreateForm, StockUpdateForm, StockSellForm
from datetime import date
import csv


# Function for handling stock insertion
@login_required
def add_stock(request):
    if request.method == "POST":
        form = StockCreateForm(request.POST)
        if form.is_valid():
            # Associate the stock with the logged-in user
            stock = form.save(commit=False)
            stock.user = request.user  # Assign the user to the stock
            stock.save()
            return redirect(
                "add_stock"
            )  # Redirect to the stock list after successful insertion
    else:
        form = StockCreateForm()

    # Fetch only the stocks for the logged-in user
    context = {
        "form": form,
        "stock_data": Stock.objects.filter(Sold=False, user=request.user).order_by(
            "SCRIP", "WACC"
        ),
        "interest": Stock.objects.filter(Sold=False, user=request.user).first(),
    }
    return render(request, "index.html", context)


@login_required
def update_stock(request, stock_id):
    stock = get_object_or_404(
        Stock, pk=stock_id, user=request.user
    )  # Ensure user has access to this stock

    if request.method == "POST":
        form = StockUpdateForm(request.POST, instance=stock)
        if form.is_valid():
            updated_stock = form.save(commit=False)

            # Update the LTP for all stocks with the same SCRIP for the logged-in user
            Stock.objects.filter(SCRIP=updated_stock.SCRIP, user=request.user).update(
                LTP=updated_stock.LTP
            )

            updated_stock.save()  # Save the updated stock, this will not trigger the WACC update logic

            return redirect("add_stock")  # Adjust the redirect URL as needed
    else:
        form = StockUpdateForm(instance=stock)

    return render(request, "stock_update.html", {"form": form})


@login_required
def delete_stock(request, stock_id):
    # Fetch the stock to be deleted, ensure it's associated with the logged-in user
    stock_to_delete = get_object_or_404(Stock, pk=stock_id, user=request.user)

    # Get the SCRIP of the stock to delete
    scrip_name = stock_to_delete.SCRIP

    # Delete the stock entry
    stock_to_delete.delete()

    # Delete other stock entries with the same SCRIP for the logged-in user
    Stock.objects.filter(SCRIP=scrip_name, user=request.user).delete()

    return redirect("add_stock")


@login_required
def sell_stock(request, stock_id):
    stock = get_object_or_404(
        Stock, pk=stock_id, user=request.user
    )  # Ensure user owns the stock

    if request.method == "POST":
        form = StockSellForm(request.POST, instance=stock)
        if form.is_valid():
            # Save the updated stock but don't commit yet
            updated_stock = form.save(commit=False)

            # Mark the stock as sold
            updated_stock.Sold = True
            updated_stock.Sold_Date = (
                date.today()
            )  # Mark the current date as the sell date
            updated_stock.save()  # Save the updated stock to the database

            # Delete other stocks with the same SCRIP that are not sellable
            Stock.objects.filter(
                SCRIP=updated_stock.SCRIP, Sellable=False, user=request.user
            ).delete()

            return redirect("sold_stock")  # Adjust this to your desired redirect URL
    else:
        form = StockSellForm(instance=stock)

    return render(request, "stock_sell.html", {"form": form})


@login_required
def sold_stocks(request):
    # Query stocks that have been marked as sold for the logged-in user
    sold_stocks = Stock.objects.filter(Sold=True, user=request.user).order_by(
        "Sold_Date", "SCRIP"
    )

    return render(request, "stock_sold.html", {"sold_stocks": sold_stocks})


@login_required
def bep_analysis(request):
    # Fetch unsold stocks for the logged-in user
    unsold_stocks = Stock.objects.filter(Sold=False, user=request.user).order_by(
        "SCRIP", "WACC"
    )

    return render(request, "bep_analysis.html", {"stock_data": unsold_stocks})


@login_required
def download_sold_stocks(request):
    # Create a CSV response
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="sold_stocks.csv"'

    writer = csv.writer(response)

    # Write the header row
    writer.writerow(
        [
            "SCRIP",
            "PURCHASED DATE",
            "MATURED DAYS",
            "QTY",
            "WACC",
            "NET INVESTMENT",
            "LTP",
            "INTEREST RATE",
            "INTEREST",
            "CURRENT VALUE",
            "CURRENT P/L",
            "SOLD AT",
            "SOLD VALUE",
            "SOLD DATE",
            "PROFIT",
            "LOSS",
            "DP",
            "PG TAX",
            "BROKER COMMISSION",
            "NET PROFIT",
            "NET LOSS",
        ]
    )

    # Write the data rows for sold stocks of the logged-in user
    sold_stocks = Stock.objects.filter(Sold=True, user=request.user).order_by(
        "Sold_Date", "SCRIP"
    )
    for stock in sold_stocks:
        writer.writerow(
            [
                stock.SCRIP,
                stock.Purchased_Date.strftime("%Y/%m/%d"),  # Format date as YYYY/MM/DD
                stock.matured_days(),
                stock.Quantity,
                format(stock.WACC if stock.WACC else stock.Purchased_At, ".2f"),
                format(stock.net_investment(), ".2f"),
                format(stock.LTP, ".2f"),
                format(stock.Interest_Rate, ".2f"),
                format(stock.interest(), ".2f"),
                format(stock.current_value(), ".2f"),
                format(stock.current_pl(), ".2f"),
                format(stock.Sold_At, ".2f") if stock.Sold_At else "",
                format(stock.sold_value(), ".2f"),
                stock.Sold_Date.strftime("%Y/%m/%d") if stock.Sold_Date else "",
                format(stock.profit_booked(), ".2f"),
                format(stock.loss_beared(), ".2f"),
                stock.dp(),
                format(stock.pg_tax(), ".2f"),
                format(stock.Broker_Commission, ".2f"),
                format(stock.net_profit(), ".2f"),
                format(stock.net_loss(), ".2f"),
            ]
        )

    return response


def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)
