import requests, uuid, json
import json

with open('./preprocessing/config.json', 'r') as file:
    config = json.load(file)


def translate( text:str, language: list) -> str: 
    # Azure Trans config
    key = config['AzureTranslate']['subscription_key']
    location = config['AzureTranslate']['region']
    endpoint = "https://api.cognitive.microsofttranslator.com"
    path = '/translate'
    constructed_url = endpoint + path

    headers = {
        'Ocp-Apim-Subscription-Key': key,
        # location required if you're using a multi-service or regional (not global) resource.
        'Ocp-Apim-Subscription-Region': location,
        'Content-type': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }

    params = {
        'api-version': '3.0',
        #'from': language,
        'to': language
    }

    body = [{'text': text}]
    request = requests.post(constructed_url, params=params, headers=headers, json=body)
    response = request.json()

    if response == None:
        raise ValueError("translator meet problems!!!")
    
    #return response[0]["translations"][0]["text"]
    return response


