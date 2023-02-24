from utils.search import get_provider


async def search_prodiver_a(request):
    return await get_provider(
        cache_key='provider_a_cache',
        file_name='response_a.json',
        time_sleep=30,
        ttl=60 * 60
    )
