import json
import os
import glob

# Bundle questions
modules = {
    'A': 'web/data/module_a_toan_dinh_luong.json',
    'B': 'web/data/module_b_lap_trinh_du_lieu.json',
    'C': 'web/data/module_c_kien_thuc_san_pham_ai.json',
    'D': 'web/data/module_d_logic_dao_duc_hanh_vi.json'
}

data = {}
for code, path in modules.items():
    with open(path, 'r', encoding='utf-8') as f:
        data[code] = json.load(f)

js_content = 'window.EMBEDDED_QUESTIONS = ' + json.dumps(data, ensure_ascii=False) + ';\n'
with open('web/data/questions-data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Generated questions-data.js: A={len(data['A'])}, B={len(data['B'])}, C={len(data['C'])}, D={len(data['D'])}")

# Bundle docs
docs = {}
for md_file in glob.glob('web/docs/*.md'):
    basename = os.path.basename(md_file)
    with open(md_file, 'r', encoding='utf-8') as f:
        docs[basename] = f.read()

docs_js = 'window.EMBEDDED_DOCS = ' + json.dumps(docs, ensure_ascii=False) + ';\n'
with open('web/docs/docs-data.js', 'w', encoding='utf-8') as f:
    f.write(docs_js)

print(f"Generated docs-data.js with {len(docs)} documents")
