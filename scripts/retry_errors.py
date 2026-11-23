import json
import requests
import time

filepath = 'results/benchmarks/kaitu_v3_200.json'
with open(filepath, 'r', encoding='utf-8') as f:
    results = json.load(f)

retry_ids = [x['id'] for x in results if x.get('error')]
print(f'Retrying {len(retry_ids)} IDs: {retry_ids}')

for entry in results:
    if entry['id'] in retry_ids:
        pid = entry['id']
        prompt = entry['prompt']
        print(f'Retrying ID {pid}: {prompt[:40]}...')
        t0 = time.time()
        payload = {
            'model': 'kaitu-v3:latest',
            'messages': [{'role': 'user', 'content': prompt}],
            'stream': False,
            'options': {'temperature': 0.3, 'top_p': 0.8}
        }
        try:
            r = requests.post('http://localhost:11434/api/chat', json=payload, timeout=120)
            elapsed = round(time.time() - t0, 3)
            if r.status_code == 200:
                data = r.json()
                entry['response'] = data.get('message', {}).get('content', '').strip()
                eval_count = data.get('eval_count', 0)
                eval_dur = data.get('eval_duration', 0)
                entry['time_seconds'] = elapsed
                entry['eval_count'] = eval_count
                entry['tokens_per_second'] = round(eval_count / (eval_dur / 1e9), 1) if eval_dur > 0 else 0
                entry['error'] = None
                print(f'  -> OK ({elapsed}s, {eval_count} tokens)')
            else:
                print(f'  -> Failed HTTP {r.status_code}')
        except Exception as e:
            print(f'  -> Exception: {e}')

with open(filepath, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print('Done updating results/benchmarks/kaitu_v3_200.json')
