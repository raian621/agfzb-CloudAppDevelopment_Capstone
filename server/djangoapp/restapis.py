import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

API_KEY = "L68tZHhxMxrz3PQhKFpjgQorf8viUjYbKta8RDfjYmeA"
NLU_URL = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/31ba689f-0bb4-45f9-8718-6c4927a080fd"

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
  try:
    response = requests.get(url, headers={"Content-Type": "application/json"}, params=kwargs)
  except:
    print("Network exception ocurred")
  
  status_code = response.status_code
  print(f"With status {status_code}")

  json_data = json.loads(response.text)
  return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
  try:
    print(json_payload)
    response = requests.post(url, json=json_payload, params=kwargs)
  except:
    print("Network exception ocurred")
  
  status_code = response.status_code
  print(f"With status {status_code}")

  json_data = json.loads(response.text)
  return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
  results = []

  json_result = get_request(url)
  if json_result:
    dealers = json_result["data"]

    for dealer in dealers:
      dealer_obj = CarDealer(
        address=dealer["address"],
        city=dealer["city"],
        full_name=dealer["full_name"],
        id=dealer["id"],
        lat=dealer["lat"],
        long=dealer["long"],
        short_name=dealer["short_name"],
        st=dealer["st"],
        zip=dealer["zip"],
      )

      results.append(dealer_obj)

  return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
  results = []

  json_result = get_request(url, kwargs={"dealerId": dealer_id})

  if json_result:
    reviews = json_result["data"]

    for review in reviews:
      review_obj = DealerReview(
        dealership=review["dealership"],
        name=review["name"],
        purchase=review["purchase"],
        review=review["review"],
        purchase_date=review["purchase_date"],
        car_make=review.get("car_make", ""),
        car_model=review.get("car_model", ""),
        car_year=review.get("car_year", ""),
        sentiment=analyze_review_sentiments(review["review"]),
        id=review.get("id", None),
      )
      results.append(review_obj)

  return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
  authenticator = IAMAuthenticator(API_KEY)
  natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator) 
  natural_language_understanding.set_service_url(NLU_URL)
  response = natural_language_understanding.analyze(language="en",text=text ,features=Features(sentiment=SentimentOptions(targets=[text]))).get_result()
  label=json.dumps(response, indent=2)
  label = response['sentiment']['document']['label'] 
  return label