from utils.search import get_provider


async def search_prodiver_b(request):
    return await get_provider(
        cache_key='provider_b_cache',
        file_name='response_b.json',
        time_sleep=60,
        ttl=60 * 60
    )
