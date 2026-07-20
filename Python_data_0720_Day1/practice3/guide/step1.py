'''
Step 1.
async / await 로 바꿔본다 (문법 익히기)
'''

# 비동기 작업(async/await)을 지원하는 모듈
import asyncio

async def fetch(item_id): # ① async 함수 정의 (비동기 함수)
    await asyncio.sleep(0.1) # ② await로 비동기 대기 (실제 시간이 흐름, 다른 작업 가능)
    return {'id': item_id, 'ok': True}

# 메인 비동기 함수
async def main():
    # fetch 함수를 실행하고 완료될 때까지 대기
    r = await fetch(1) # 코루틴은 await 해야 실행됨 (async def로 정의된 함수를 실제로 동작시키는 것)
    print(r)

asyncio.run(main()) # ③ 비동기 프로그램 진입점 (이벤트 루프 시작)
