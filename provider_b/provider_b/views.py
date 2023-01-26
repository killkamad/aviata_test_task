import sys

sys.path.append('../')
from utils import get_provider_data


async def search_prodiver_b(request):
    return await get_provider_data(request=request,
                                   cache_key='provider_b_cache',
                                   file_name='response_b.json',
                                   time_sleep=60,
                                   ttl=60 * 60)
