"""
Cloud function used to add reviews to the Cloudant database
"""

from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1
import requests


def main(param_dict):
    """
    adds a review to the Cloudant database
    
    - POST <domain>/api/review
    {
        "review": { data... }
    }
    """
    auth = IAMAuthenticator(apikey=param_dict["IAM_API_KEY"])
    client = CloudantV1(authenticator=auth)
    client.authenticator = auth
    client.set_service_url(param_dict["COUCH_URL"])

    result = None

    try:
        result = client.post_document(
            db=param_dict["COUCH_DATABASE"],
            document=param_dict["review"]
        ).get_result()
    except ApiException as api_exception:
        print("unable to connect", api_exception)
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
