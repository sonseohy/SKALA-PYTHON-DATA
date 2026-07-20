'''
Step 3.
백프레셔 — Semaphore 로 동시 요청 수 제한
'''

import asyncio

MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT) # 입장권 10장

async def fetch_limited(item_id):
    async with sem: # ★ 입장권 받기 (없으면 대기)
        await asyncio.sleep(0.1)
        return {'id': item_id, 'ok': True}
    # with 블록을 나가면 입장권 자동 반납

async def main():
    # asyncio.gather : 여러 비동기 작업을 동시에 실행하고 모든 결과를 기다림
    # fetch_limited(i) : 동시 요청 수를 제한하면서 각 item을 가져오는 코루틴
    # * : 리스트를 개별 인자로 변환 (언팩/unpacking)
    results = await asyncio.gather(*[fetch_limited(i) for i in range(60)])
    return results
