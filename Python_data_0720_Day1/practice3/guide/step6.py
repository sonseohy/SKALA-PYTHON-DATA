'''
Step 6.
예외 격리 — 하나 실패해도 전체는 살리기
'''

import asyncio

MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT)

# 세마포어로 동시 실행 수를 제한하며 데이터를 가져오는 함수 (id=5는 실패 상황)
async def fetch_limited(item_id):
    async with sem:
        if item_id == 5: # 실패 상황을 흉내
            raise ValueError('boom')
        await asyncio.sleep(0.1)
        return {'id': item_id, 'ok': True}

# 60건을 동시에 실행하고, 실패해도 나머지 결과는 살리는 함수
async def main():
    tasks = [fetch_limited(i) for i in range(60)]
    # return_exceptions=True: 하나가 실패해도 gather 전체가 죽지 않고 예외를 결과로 받음
    results = await asyncio.gather(*tasks, return_exceptions=True)
    ok = [r for r in results if not isinstance(r, Exception)] # 성공한 결과만
    fail = [r for r in results if isinstance(r, Exception)] # 실패(예외)만
    print(f'성공 {len(ok)}건 / 실패 {len(fail)}건')

asyncio.run(main())
