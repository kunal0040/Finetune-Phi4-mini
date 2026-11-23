import json

with open('results/benchmarks/kaitu_v4_200.json', 'r', encoding='utf-8') as f:
    v4 = json.load(f)

kaitu_count = sum(1 for item in v4 if 'kaitu' in item['response'].lower())
kunal_count = sum(1 for item in v4 if 'kunal' in item['response'].lower())
phi_count = sum(1 for item in v4 if 'phi' in item['response'].lower() or 'microsoft' in item['response'].lower())
ai_boilerplate = sum(1 for item in v4 if any(s in item['response'].lower() for s in ['as an ai', "i'm just a", 'digital assistant', 'language model']))
lengths = [item.get('eval_count', len(item['response'].split())) for item in v4]
avg_len = sum(lengths) / len(lengths)
empty_count = sum(1 for item in v4 if not item['response'].strip())

print(f"Total evaluated: {len(v4)}")
print(f"Mentions Kaitu: {kaitu_count}")
print(f"Mentions Kunal: {kunal_count}")
print(f"Mentions Phi / Microsoft: {phi_count}")
print(f"Generic AI boilerplate: {ai_boilerplate}")
print(f"Avg tokens (eval_count): {avg_len:.1f}")
print(f"Empty responses: {empty_count}")

targets = [1, 2, 4, 6, 7, 33, 36, 44, 46, 58, 76, 167, 179]
print("\n--- KEY PROMPT RESPONSES ---")
for item in v4:
    if item['id'] in targets:
        print(f"ID #{item['id']} [{item['category']}]")
        print(f"Prompt: {item['prompt']}")
        print(f"Response: {item['response']}")
        print("-" * 50)
