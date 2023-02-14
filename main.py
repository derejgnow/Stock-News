import requests as rq
import os
import datetime as dt
import twilio.rest


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

# Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

news_params = {
    'q': COMPANY_NAME,
    'apiKey': os.environ.get('news_API'),
    'searchIn': 'title,content',
    'language': 'en',
}
news_response = rq.get('https://newsapi.org/v2/everything', params=news_params)
news_response.raise_for_status()
news_data = news_response.json()
articles = [(item['title'], item['description']) for item in news_data['articles'][:3]]

# Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
TWILIO_PHONE = '+17087227150'
MY_PHONE = '+6582288912'
account_sid = os.environ.get('twilio_SID')
auth_token = os.environ.get('twilio_auth_token')
client = twilio.rest.Client(account_sid, auth_token)


def price_increase(percentage):
    message = client.messages.create(from_=TWILIO_PHONE,
                                     body=f'{STOCK}: 📈{round(percentage)}%\n\nHeadline: {articles[0][0]}'
                                          f'\n\nBrief: {articles[0][1]}',
                                     to=MY_PHONE
                                     )
def price_decrease(percentage):
    message = client.messages.create(from_=TWILIO_PHONE,
                                     body=f'{STOCK}: 📉{round(percentage)}%\n\nHeadline: {articles[0][0]}'
                                          f'\n\nBrief: {articles[0][1]}',
                                     to=MY_PHONE
                                     )

#TODO.1: what if weekend (repeated)

# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stock_param = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': os.environ.get('stock_API_key')
}
stock_response = rq.get('https://www.alphavantage.co/query', params=stock_param)
stock_response.raise_for_status()
stock_data = stock_response.json()

# form a list of relevant closing prices (yesterday and the day before)
relevant_days = [(key, value) for (key, value) in stock_data['Time Series (Daily)'].items()][:2]
relevant_prices = [value['4. close'] for (key, value) in relevant_days]

yesterday_close = float(relevant_prices[0])
day_before_close = float(relevant_prices[1])
price_change = yesterday_close / day_before_close

if price_change >= 1.05:
    price_increase(price_change)
elif price_change <= 0.95:
    price_decrease(price_change)



# Format the SMS message like this:
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

