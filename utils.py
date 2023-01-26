from functools import reduce
from lxml import etree
import aiofiles
import json
import aiohttp
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime
import asyncio


# async read file
async def read_json_file(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        json_data = await f.read()
    return json_data


# Get provider from cache or read file, save data in cache in return provider data
async def get_provider_data(request, cache_key, file_name, time_sleep, ttl):
    json_data = cache.get(cache_key)
    if not json_data:
        json_data = await read_json_file(file_name)
        cache.set('provider_a_cache', json_data, ttl)
    await asyncio.sleep(time_sleep)
    return JsonResponse(json.loads(json_data), safe=False)


# Sending http request
async def fetch(client, url, response_type='json', request_type='get'):
    if request_type == 'get':
        async with client.get(url) as response:
            if response.status != 200:
                response.raise_for_status()
            if response_type == 'text':
                return await response.text()
            else:
                return await response.json()
    else:
        async with client.post(url) as response:
            if response.status != 200:
                response.raise_for_status()
            if response_type == 'text':
                return await response.text()
            else:
                return await response.json()


# Create tasks -> send http requests -> combine request data -> save in redis cache
async def fetch_providers_and_save_results(search_id, url_list):
    async with aiohttp.ClientSession() as client:
        tasks = []
        for url in url_list:
            task = asyncio.ensure_future(fetch(client, url, 'json', 'post'))
            tasks.append(task)
        results = await asyncio.gather(*tasks)

    ttl = 60 * 60
    combined_results = reduce(lambda a, b: a + b, results)
    cache.set(search_id, json.dumps(combined_results), ttl)


async def fetch_currencies():
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


async def download_currency_rates_daily():
    await fetch_currencies()


