'''
확장 과제
dead-letter 격리 — 재시도까지 실패한 건은 dead_letter.json에 저장
'''

import asyncio
import json

MAX_CONCURRENT = 10
sem = asyncio.Semaphore(MAX_CONCURRENT)

# 항상 실패하는 요청을 흉내 (dead-letter 데모용, id=5만 실패)
async def do_request(item_id):
    if item_id == 5:
        raise ValueError('boom')
    await asyncio.sleep(0.1)
    return {'id': item_id, 'ok': True}

# 실패하면 지수 백오프로 재시도, 그래도 실패하면 실패 결과를 반환
async def fetch_retry(item_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            async with sem:
                return await do_request(item_id)
        except Exception as e:
            if attempt == max_retries - 1: # 마지막 시도까지 실패
                return {'id': item_id, 'ok': False, 'error': str(e)}
            wait = 2 ** attempt # 1 → 2 → 4 초로 대기 시간 증가
            await asyncio.sleep(wait)

# 60건을 동시에 재시도 처리하고, 끝까지 실패한 건만 dead_letter.json에 격리
async def main():
    results = await asyncio.gather(*[fetch_retry(i) for i in range(60)]) # 60건 동시 실행
    dead_letters = [r for r in results if not r['ok']] # 재시도까지 실패한 건만 모음

    # 실패를 조용히 삼키지 않고 별도 파일에 기록
    with open('dead_letter.json', 'w', encoding='utf-8') as f:
        json.dump(dead_letters, f, ensure_ascii=False, indent=2)

    print(f'성공 {len(results) - len(dead_letters)}건 / dead-letter {len(dead_letters)}건')

asyncio.run(main())
