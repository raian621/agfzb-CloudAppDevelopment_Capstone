from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
import requests

def main(param_dict):
  auth = IAMAuthenticator(apikey=param_dict["IAM_API_KEY"])
  client = CloudantV1(authenticator=auth)
  client.authenticator = auth
  client.set_service_url(param_dict["COUCH_URL"])
  
  result = None
  selector = {}

  if "dealerId" in param_dict:
    selector["dealership"] = {
      "$eq": param_dict["dealerId"]
    }

  try:
    result = client.post_find(db=param_dict["COUCH_DATABASE"], limit=10, selector=selector).get_result()["docs"]
  except ApiException as ae:
    print("unable to connect", ae)
    return {
      'statusCode': 404,
      'message': 'Something went wrong'
    }
  except (requests.exceptions.RequestException, ConnectionResetError) as err:
    print("connection error", err)
    return {
      'statusCode': 404,
      'message': 'Something went wrong'
    }
  
  return {
    "headers": { "Content-Type":"application/json" },
    "body": { "data": result }
  }
