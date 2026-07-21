'''
Step 5.
재시도 — 지수 백오프(exponential backoff)
'''

import asyncio

MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT)

# do_request: 실제 요청을 보내는 함수 자리 (모의 실행)
async def do_request(item_id):
    await asyncio.sleep(0.1) # 네트워크 대기를 흉내
    return {'id': item_id, 'ok': True}

# 실패하면 지수 백오프(1→2→4초)로 대기 후 재시도
async def fetch_retry(item_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with sem:
                return await do_request(item_id)
        except Exception as e:
            if attempt == max_retries - 1: # 마지막 시도였으면 포기
                return {'id': item_id, 'ok': False, 'error': str(e)}
            wait = 2 ** attempt # 1 → 2 → 4 초
            print(f'{item_id} 실패, {wait}초 후 재시도')
            await asyncio.sleep(wait)

async def main():
    result = await fetch_retry(1)
    print(result)

asyncio.run(main())
