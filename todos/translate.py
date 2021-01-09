import os
import json

from todos import decimalencoder
import boto3

dynamodb = boto3.resource('dynamodb')
comprehend = boto3.client('comprehend')
translate = boto3.client('translate')

def gettranslate(event, context):
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])

    # fetch todo from the database
    result = table.get_item(
        Key={
            'id': event['pathParameters']['id']
        }
    )

    response_lang = comprehend.detect_dominant_language(Text=result['Item']['text'])
    
    slang = response_lang['Languages'][0]['LanguageCode']
    
    result_translate = translate.translate_text(Text=result['Item']['text'], SourceLanguageCode=slang, TargetLanguageCode=event['pathParameters']['language'])
    
    result['Item']['text'] = result_translate.get('TranslatedText')
    
    # create a response
    response = {
        "statusCode": 200,
        "body": json.dumps(result['Item'],
                           cls=decimalencoder.DecimalEncoder)
    }
    
    return response