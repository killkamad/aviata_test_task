import json
import aiohttp
import asyncio
from django.core.cache import cache
from lxml import etree
from datetime import datetime

from utils.search import fetch


async def get_rates():
    currencies = cache.get('currencies')
    if not currencies:
        currencies = await update_from_national_bank()
    else:
        currencies = json.loads(currencies)
    return currencies


def add_price_and_recalculate(providers_data, currencies, currency):
    for item in providers_data:
        item_currency = item['pricing']['currency']
        item_total = float(item['pricing']['total'])

        if item_currency != 'KZT':
            converted_to_kzt = item_total * float(currencies[item_currency])
        else:
            converted_to_kzt = item_total

        if currency != 'KZT':
            amount = converted_to_kzt / float(currencies[currency])
        else:
            amount = converted_to_kzt

        item['price'] = {
            "amount": f'{amount:.2f}',
            "currency": currency
        }

    return providers_data


async def update_from_national_bank():
    date_time = datetime.now().strftime("%d.%m.%Y")
    bank_url = f'https://www.nationalbank.kz/rss/get_rates.cfm?fdate={date_time}'

    async with aiohttp.ClientSession() as client:
        task = asyncio.ensure_future(fetch(client, bank_url, 'text', 'get'))
        xml_data = await task
    root = etree.fromstring(xml_data.encode())
    currency_dict = {}
    for currency in root.getchildren():
        cur_title = ''
        cur_description = ''
        for elem in currency.getchildren():
            if elem.tag == 'title':
                cur_title = elem.text
            if elem.tag == 'description':
                cur_description = elem.text
            if cur_title and cur_description:
                currency_dict[cur_title] = cur_description
                continue
    cache.set('currencies', json.dumps(currency_dict))
    return currency_dict
