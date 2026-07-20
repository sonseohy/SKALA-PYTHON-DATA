'''
Step 0.
동기 버전을 먼저 만들고 시간을 잰다
'''

import time

def fetch_sync(item_id):
    time.sleep(0.1) # 네트워크 대기 흉내
    return {'id': item_id, 'ok': True}

start = time.perf_counter() # 현재 시간을 고정밀 타이머로 기록
results = [fetch_sync(i) for i in range(60)]
print(f'동기: {time.perf_counter() - start:.2f}초')