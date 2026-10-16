import json

with open('web/data/questions-data.js', 'r', encoding='utf-8') as f:
    text = f.read()

prefix = 'window.EMBEDDED_QUESTIONS = '
if text.startswith(prefix):
    text = text[len(prefix):].rstrip(';\n ')

data = json.loads(text)
missing = []
for mod, qlist in data.items():
    for q in qlist:
        if 'question' not in q or q['question'] is None:
            missing.append((q.get('id', 'unknown'), list(q.keys())))

print(f"Total questions with missing 'question' field: {len(missing)}")
for item in missing[:10]:
    print(item)
