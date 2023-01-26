import sys

sys.path.append('../')
from utils import get_provider_data


async def search_prodiver_a(request):
    return await get_provider_data(request=request,
                                   cache_key='provider_a_cache',
                                   file_name='response_a.json',
                                   time_sleep=30,
                                   ttl=60 * 60)
