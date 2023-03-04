from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarMake, CarModel
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

CF_URL_BASE = "https://us-south.functions.appdomain.cloud/api/v1/web/2df01edb-4ddf-4eb7-bb00-54036390fa19/dealership-package"
dealerships = None

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create an `about` view to render a static about page
def about(request):
    if request.method == "GET":
        return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
    if request.method == 'GET':
        return render(request, "djangoapp/contact.html")

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "Invalid username or password."
            return render(request, request.path, context)
    else:
        # if request.user.is_authenticated:
        # return render(request, 'djangoapp:index', context)
        return redirect('djangoapp:index')


# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']

        user_exists = False

        try:
            User.objects.get(username=username)
            user_exists = True
        except:
            logger.error("New user")

        if not user_exists:
            user = User.objects.create_user(
                username=username, 
                first_name=firstname,
                last_name=lastname,
                password=password
            )
            login(request, user)
            return redirect('djangoapp:index')
        else:
            context['message'] = "User already exists."
            return render(request, request.path, context)
    else:
        return render(request, 'djangoapp/registration.html')

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    global dealerships
    context = {}
    if request.method == "GET":
        url = f"{CF_URL_BASE}/get-dealership"
        if (dealerships == None):
            dealerships = get_dealers_from_cf(url)
        context["dealers"] = dealerships
        return render(request, "djangoapp/index.html", context)

# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealer_id):
    dealer = get_dealers_from_cf(f"{CF_URL_BASE}/get-dealership", dealerId=dealer_id)[0]
    context = {"dealer": dealer}

    if request.method == "GET":
        url = f"{CF_URL_BASE}/get-review"
        print(f"-- GET DEALER DETAILS: {url}")
        context["reviews"] = get_dealer_reviews_from_cf(url, dealer_id)

        return render(request, "djangoapp/dealer_details.html", context)
        

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    dealer = get_dealers_from_cf(f"{CF_URL_BASE}/get-dealership", dealerId=dealer_id)[0]
    context = {"dealer": dealer}
    if request.method == "POST":
        user = request.user
        post_data=request.POST
        review = {
            'dealership': dealer_id,
            'name': f"{user.first_name} {user.last_name}",
            'purchase_date': post_data['purchase_date'],
            'review': post_data['review'],
            'purchase': post_data.get('purchase', False) == 'on',
        }

        if review['purchase']:
            print(post_data['car'])
            car = CarModel.objects.get(id=int(post_data['car']))
            print("car:", car)
            print("car:", car.car_make.name)
            print("car:", car.name)
            print("car:", car.year)
            review['car_make'] =  car.car_make.name
            review['car_model'] = car.name
            review['car_year'] =  car.year

        print(review)

        json_payload = { "review": review }
        url = f'{CF_URL_BASE}/post-review'
        post_request(url, json_payload, dealer_id=dealer_id)

        return redirect(f'/djangoapp/dealer/{dealer_id}')
    else:
        cars = []
        for model in CarModel.objects.filter(dealer_id=dealer.id):
            cars.append({
                'id': model.id,
                'year': model.year,
                'name': model.name,
                'make': model.car_make.name
            })
        context['cars'] = cars
        print(cars)
        return render(request, "djangoapp/add_review.html", context)

