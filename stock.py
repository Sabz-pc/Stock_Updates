import json
import os
import boto3
import requests

def lambda_handler(event, context):
    # Alpha Vantage API key and base URL setup
    api_key = os.getenv('F7YDSV02S99SZGSO')
    base_url = "https://www.alphavantage.co/query"

    # List of stock symbols
    symbols = ['IBM', 'Nestle India'] #add your stocks names 
    table_data = []

    for symbol in symbols:
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": api_key
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            time_series = data.get('Time Series (Daily)', {})
            latest_date = max(time_series.keys(), default=None)
            if latest_date:
                latest_close = time_series[latest_date].get('4. close')
                if latest_close:
                    table_data.append(f"{symbol}: ₹{latest_close} as of {latest_date}")
                else:
                    table_data.append(f"{symbol}: No closing data available")
            else:
                table_data.append(f"{symbol}: No data available")
        except Exception as e:
            table_data.append(f"{symbol}: Error fetching data - {e}")

    # Serialize table_data
    message_content = "\n".join(table_data)
    
    # SNS client setup
    sns_client = boto3.client('sns', region_name='us-west-2') #add your  region 
    topic_arn = 'arn:aws:sns:us-west-2:771878427139:test-price'                                  #add your aws sns topic  arn 
    
    try:
        # Publish the message to SNS
        response = sns_client.publish(
            TopicArn=topic_arn,
            Message=message_content,
            Subject='Stock Prices Update'
        )
        return {
            "statusCode": 200,
            "body": "Message published to SNS successfully!"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": "Failed to publish message: " + str(e)
        }
