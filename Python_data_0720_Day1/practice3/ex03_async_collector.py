import time
import json
import asyncio

USE_REAL_HTTP = False   # True로 바꾸면 httpx로 실제 HTTP 요청을 보냄 (모의 실행 기본값)
TOTAL_ITEMS = 60
MAX_CONCURRENT = 10     # 백프레셔: 동시 요청 수 제한
MAX_RETRIES = 3
REQUEST_TIMEOUT = 3.0   # 요청별 타임아웃(초)
FAIL_ONCE_ID = 5        # 이 id는 첫 시도만 일부러 실패시켜 재시도 동작을 시연

sem = asyncio.Semaphore(MAX_CONCURRENT)


# 실제 요청 한 번 보냄. FAIL_ONCE_ID는 첫 시도만 실패시킴
async def do_request(item_id, client, attempt):
    if USE_REAL_HTTP:
        resp = await client.get('https://httpbin.org/get', params={'id': item_id})
        resp.raise_for_status()
        return {'id': item_id, 'ok': True}

    await asyncio.sleep(0.1)  # 네트워크 대기 상황
    if item_id == FAIL_ONCE_ID and attempt == 0:
        raise ValueError('boom')  # 일시적 실패 상황
    return {'id': item_id, 'ok': True}


# 백프레셔와 타임아웃을 적용해 요청하고, 실패하면 지수 백오프로 재시도
async def fetch_retry(item_id, client=None, max_retries=MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            async with sem:  # ★ 입장권 없으면 대기 (백프레셔)
                async with asyncio.timeout(REQUEST_TIMEOUT):  # ★ 타임아웃
                    return await do_request(item_id, client, attempt)
        except TimeoutError:
            if attempt == max_retries - 1:
                return {'id': item_id, 'ok': False, 'error': 'timeout'}
        except Exception as e:
            if attempt == max_retries - 1:  # 마지막 시도까지 실패하면 포기
                return {'id': item_id, 'ok': False, 'error': str(e)}
            wait = 2 ** attempt  # 지수 백오프: 1 -> 2 -> 4초
            print(f'  {item_id}번 실패, {wait}초 후 재시도')
            await asyncio.sleep(wait)


# 60건을 동시에 실행하고, 하나가 실패해도 나머지 결과는 살린다(예외 격리).
async def collect(client=None):
    tasks = [fetch_retry(i, client) for i in range(TOTAL_ITEMS)]
    # return_exceptions=True: 하나가 실패해도 gather 전체가 죽지 않도록 예외 격리
    return await asyncio.gather(*tasks, return_exceptions=True)


# 전체 수집을 실행하고, 재시도까지 실패한 건은 dead_letter.json에 격리
async def main():
    if USE_REAL_HTTP:
        import httpx
        async with httpx.AsyncClient() as client:
            results = await collect(client)
    else:
        results = await collect()

    ok = [r for r in results if isinstance(r, dict) and r.get('ok')]
    dead_letters = [r for r in results if not (isinstance(r, dict) and r.get('ok'))]

    # 실패를 별도 파일에 격리
    with open('dead_letter.json', 'w', encoding='utf-8') as f:
        json.dump(dead_letters, f, ensure_ascii=False, indent=2, default=str)

    print(f'성공 {len(ok)}건 / dead-letter {len(dead_letters)}건')


if __name__ == '__main__':
    start = time.perf_counter()
    asyncio.run(main())
    elapsed = time.perf_counter() - start

    print(f'처리량: {TOTAL_ITEMS}건 ≈ {elapsed:.2f}초')
    print(f'(동기 실행이었다면 약 {TOTAL_ITEMS * 0.1:.1f}초 - 대기시간 중첩 제거로 단축됨)')
