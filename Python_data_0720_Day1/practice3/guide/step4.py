'''
Step 4.
타임아웃 — 무한정 기다리지 않기
'''

import asyncio

MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT)

async def fetch_with_timeout(item_id):
    async with sem:
        try:
            async with asyncio.timeout(3.0): # 3초 넘으면 포기
                await asyncio.sleep(0.1)
                return {'id': item_id, 'ok': True}
        except TimeoutError:
            return {'id': item_id, 'ok': False, 'reason': 'timeout'}
