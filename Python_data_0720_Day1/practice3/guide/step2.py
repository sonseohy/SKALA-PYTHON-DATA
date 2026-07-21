'''
Step 2.
gather 로 60개를 '동시에' 던지기
'''

import time
import asyncio

async def fetch(item_id):
    await asyncio.sleep(0.1)
    return {'id': item_id, 'ok': True}

async def main():
    tasks = [fetch(i) for i in range(60)] # 아직 실행 안 됨 (예약만)
    results = await asyncio.gather(*tasks) # ★ 여기서 한꺼번에 실행
    print(len(results))

start = time.perf_counter()
asyncio.run(main())
print(f'비동기: {time.perf_counter() - start:.2f}초') # 약 0.1초!
