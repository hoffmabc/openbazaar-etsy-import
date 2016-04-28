#!/usr/bin/env python

import base64
import csv
import os
import requests
import sqlite3
import threading
import urllib

api = 'http://localhost:18469/api/v1'
OB_USERNAME="username"
OB_PASSWORD="password"


currency_codes = ("AED", "ARS", "AUD", "BRL", "CAD", "CHF", "CNY", "CZK", "DKK", "EUR", "GBP", "HKD", "HUF", "ILS",
                  "INR", "JPY", "KRW", "MAD", "MXN", "NOK", "NZD", "PHP", "PLN", "RUB", "SEK", "SGD", "THB", "TRY",
                  "USD", "ZAR")

with open('listings.csv', 'rU') as f:
    reader = csv.DictReader(f, delimiter=',')

    #listing_count = sum(1 for listing in reader)

    # if listing_count >= 1:
    s = requests.Session()
    payload = {'username': OB_USERNAME, 'password': OB_PASSWORD}
    login = s.post('%s/login' % api, data=payload)
    print login.json()

    for listing in reader:
        print listing

        # Download images from listing
        image = urllib.urlopen(listing['IMAGE1'])
        image_64 = base64.encodestring(image.read())

        # Insert listing into OB
        payload = {
            'keywords': listing['TAGS'],
            'title': listing['TITLE'],
            'description': listing['DESCRIPTION'],
            'currency_code': listing['CURRENCY_CODE'],
            'price': listing['PRICE'],
            'process_time': 'TBD',
            'images': [image_64],
            'expiration_date': '',
            'metadata_category': 'physical good',
            'nsfw': 'false',
            'terms_conditions': '',
            'returns': '',
            'shipping_currency_code': listing['CURRENCY_CODE'],
            'shipping_domestic': '',
            'shipping_international': '',
            'category': '',
            'condition': '',
            'sku': '',
            'free_shipping': 'false'
        }
        posted = s.post('%s/contracts' % api, data=payload)
        print posted.json()