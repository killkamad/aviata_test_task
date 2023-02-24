import json
import uuid
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from airflow.celery_tasks import sync_fetch_providers_and_save_results
from utils.currencies import get_rates, add_price_and_recalculate


async def fetch_from_providers(request):
    search_id = str(uuid.uuid4())
    url_list = [
        settings.PROVIDER_A_URL, settings.PROVIDER_B_URL
    ]
    sync_fetch_providers_and_save_results.delay(search_id, url_list)

    return JsonResponse({'search_id': search_id})


async def get_providers_data_with_currency_prices(request, search_id, currency):
    currency = currency.upper()
    completed_data = cache.get(f'{search_id}-{currency}')
    if not completed_data:
        providers_data = cache.get(search_id, [])
        if providers_data:
            status = 'COMPLETED'
            providers_data = json.loads(providers_data)
            currencies = await get_rates()
            providers_data = add_price_and_recalculate(providers_data, currencies, currency)
            providers_data.sort(key=lambda item: float(item['price']['amount']))
            cache.set(f'{search_id}-{currency}', json.dumps(providers_data), 60 * 60 * 24)
        else:
            status = 'PENDING'
    else:
        providers_data = json.loads(completed_data)
        status = 'COMPLETED'

    return JsonResponse({
        'search_id': search_id,
        'status': status,
        'items': providers_data
    })

