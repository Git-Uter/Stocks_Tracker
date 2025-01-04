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
            # Create the stock instance without saving it immediately
            stock = form.save(commit=False)
            stock.user = request.user  # Associate the stock with the logged-in user
            stock.SCRIP = stock.SCRIP.upper()  # Ensure SCRIP is in uppercase

            # Step 1: Check for existing duplicates for the same user and same SCRIP
            duplicates = Stock.objects.filter(
                SCRIP=stock.SCRIP, Sold=False, user=request.user
            )

            if duplicates.exists():
                # Step 2: Handle duplicates by adjusting the first record found
                existing_stock = duplicates.first()

                # Step 3: Recalculate WACC (Weighted Average Cost of Capital)
                new_wacc = calculate_new_wacc(duplicates, stock)

                # Step 4: Calculate the total net investment and weighted interest rate
                total_net_investment = (
                    sum(dup.net_investment() for dup in duplicates)
                    + stock.net_investment()
                )
                total_weighted_interest = sum(
                    dup.Interest_Rate * dup.net_investment() for dup in duplicates
                ) + (stock.Interest_Rate * stock.net_investment())

                # Calculate the weighted average interest rate (WHT_Interest_Rate)
                WHT_Interest_Rate = (
                    total_weighted_interest / total_net_investment
                    if total_net_investment > 0
                    else 0
                )

                # Step 5: Update the existing stock record with the new values
                existing_stock.Quantity += stock.Quantity
                existing_stock.WACC = new_wacc
                existing_stock.Interest_Rate = WHT_Interest_Rate
                existing_stock.LTP = stock.LTP
                existing_stock.Broker_Commission = stock.Broker_Commission

                # Save the updated existing stock
                existing_stock.save()

                # Step 6: Skip creating a new stock, since we've adjusted the existing one
                return redirect("add_stock")

            # Step 7: If no duplicates found, save the new stock normally
            stock.save()

            # Redirect back to the stock list page
            return redirect("add_stock")

    else:
        form = StockCreateForm()

    # Fetch all the stocks for the logged-in user that are not sold
    context = {
        "form": form,
        "stock_data": Stock.objects.filter(Sold=False, user=request.user).order_by(
            "SCRIP", "WACC"
        ),
    }
    return render(request, "index.html", context)


def calculate_new_wacc(duplicates, stock):
    """
    Calculate the new WACC (Weighted Average Cost of Capital) based on existing duplicates and the new stock.
    """
    total_value = sum(dup.Quantity * dup.WACC for dup in duplicates) + (
        stock.Quantity * stock.WACC
    )
    total_quantity = sum(dup.Quantity for dup in duplicates) + stock.Quantity
    if total_quantity == 0:
        return 0
    return total_value / total_quantity


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

    # Delete the stock entry
    stock_to_delete.delete()

    return redirect("add_stock")


@login_required
def sell_stock(request, stock_id):
    # Retrieve the stock owned by the user
    stock = get_object_or_404(Stock, pk=stock_id, user=request.user)

    if request.method == "POST":
        form = StockSellForm(request.POST)

        if form.is_valid():
            sold_quantity = form.cleaned_data["Quantity"]
            sold_price = form.cleaned_data["Sold_At"]
            broker_commission = form.cleaned_data["Broker_Commission"]

            # Check if the user has enough stock
            if sold_quantity > stock.Quantity:
                form.add_error(
                    "Quantity",
                    "Sold quantity cannot be greater than available quantity.",
                )
                return render(request, "stock_sell.html", {"form": form})

            # Print the stock quantity details for debugging
            print("Stock quantity before sale:", stock.Quantity)
            print("Stock quantity to be sold:", sold_quantity)

            # Update the stock quantity after sale
            updated_quantity = stock.Quantity - sold_quantity
            stock.Quantity = updated_quantity

            # If the stock quantity becomes 0, delete the stock entry
            if stock.Quantity == 0:
                print(f"Stock quantity is now 0, deleting stock with ID {stock_id}.")
                stock.delete()
            else:
                # Otherwise, save the updated stock instance
                stock.save()

            # Create a new instance for the sold stock entry
            sold_stock = Stock(
                user=stock.user,
                SCRIP=stock.SCRIP,
                WACC=stock.WACC,
                Purchased_Date=stock.Purchased_Date,
                Interest_Rate=stock.Interest_Rate,
                Quantity=sold_quantity,
                LTP=stock.LTP,
                Sold=True,
                Sellable=False,
                Sold_At=sold_price,
                Sold_Date=date.today(),
                Broker_Commission=broker_commission,
            )

            # Save the new sold stock instance
            print(
                f"Creating sold stock with quantity: {sold_stock.Quantity}, sold at: {sold_stock.Sold_At}"
            )
            sold_stock.save()

            # Redirect to the page showing sold stocks
            return redirect("sold_stock")  # Adjust this URL to your desired redirect
        else:
            print("Form errors:", form.errors)

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
