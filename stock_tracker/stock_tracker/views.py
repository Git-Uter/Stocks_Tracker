# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after successful registration
            return redirect(
                "login"
            )  # Redirect to a homepage or dashboard (you can change 'home' to another view)
    else:
        form = UserCreationForm()  # Display an empty form

    return render(request, "registration/register.html", {"form": form})


def home(request):
    # Check if the user is authenticated (logged in)
    if request.user.is_authenticated:
        # Redirect to 'add_stock' page if the user is logged in
        return redirect(
            "add_stock"
        )  # Replace 'add_stock' with the actual URL name of the page
    # Otherwise, render the landing page
    return render(request, "landing_page.html")
