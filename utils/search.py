import json
import aiohttp
import asyncio
from functools import reduce
from django.http import JsonResponse
from django.core.cache import cache
from utils.utils import read_json_file


# Get provider from cache or read file, save data in cache in return provider data
async def get_provider(cache_key, file_name, time_sleep, ttl):
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
        tasks = [fetch(client, url, 'json', 'post') for url in url_list]
        results = await asyncio.gather(*tasks)

    ttl = 60 * 60
    combined_results = reduce(lambda a, b: a + b, results)
    cache.set(search_id, json.dumps(combined_results), ttl)
