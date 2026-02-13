from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests

@api_view(['GET'])
def get_hadith(request):
    HADITH_API_URL = "https://hadithapi.com/api/hadiths"
    API_KEY = "$2y$10$d4nL2E660zHHBrwTB7Bviu3WvW5sToLRBWFbJ1yhn7rJzSuNpA0S"

    # Copy all query params and add the apiKey
    params = request.query_params.copy()
    params['apiKey'] = API_KEY

    try:
        api_response = requests.get(HADITH_API_URL, params=params, timeout=10)
        return Response(api_response.json(), status=api_response.status_code)
    except requests.RequestException as e:
        return Response({"error": "Failed to fetch data from Hadith API", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY) 