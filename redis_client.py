from redis.asyncio import Redis

async def get_redis():
    return Redis(host='172.27.181.101', port=6379, db=0, decode_responses=True)  
    await redis.ping()
    return redis