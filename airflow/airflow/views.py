import json
from django.http import JsonResponse
from django.core.cache import cache
import binascii
import os
import asyncio
from utils import fetch_providers_and_save_results, fetch_currencies, add_price_and_recalculate


async def fetch_data_from_providers(request):
    search_id = binascii.hexlify(os.urandom(20)).decode()
    url_list = json.loads(request.body).get('urls_list')
    asyncio.create_task(fetch_providers_and_save_results(search_id, url_list))

    return JsonResponse({'search_id': search_id})


async def get_provider_results(request, search_id, currency):
    currency = currency.upper()
    completed_data = cache.get(f'{search_id}-{currency}')
    if not completed_data:
        cache_status = False
        currencies = cache.get('currencies')
        if not currencies:
            currencies = await fetch_currencies()
        else:
            currencies = json.loads(currencies)

        providers_data = cache.get(search_id, [])
        if providers_data:
            status = 'COMPLETED'
            providers_data = json.loads(providers_data)
            providers_data = add_price_and_recalculate(providers_data, currencies, currency)
            providers_data.sort(key=lambda item: float(item['price']['amount']))
            cache.set(f'{search_id}-{currency}', json.dumps(providers_data), 60 * 60 * 24)
        else:
            status = 'PENDING'
    else:
        cache_status = True
        providers_data = json.loads(completed_data)
        status = 'COMPLETED'

    return JsonResponse({
        'search_id': search_id,
        'cache': cache_status,
        'status': status,
        'items': providers_data
    })
