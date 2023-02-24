import aiofiles


# async read file
async def read_json_file(file_path):
    async with aiofiles.open(file_path, 'r') as f:
        json_data = await f.read()
    return json_data
