import os
import urllib.request

VENDOR_DIR = "D:/proj/web/vendor"
os.makedirs(f"{VENDOR_DIR}/katex/fonts", exist_ok=True)
os.makedirs(f"{VENDOR_DIR}/prism", exist_ok=True)
os.makedirs(f"{VENDOR_DIR}/marked", exist_ok=True)
os.makedirs(f"{VENDOR_DIR}/lucide", exist_ok=True)

files = [
    # KaTeX
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css", f"{VENDOR_DIR}/katex/katex.min.css"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js", f"{VENDOR_DIR}/katex/katex.min.js"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js", f"{VENDOR_DIR}/katex/auto-render.min.js"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/fonts/KaTeX_Main-Regular.woff2", f"{VENDOR_DIR}/katex/fonts/KaTeX_Main-Regular.woff2"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/fonts/KaTeX_Math-Italic.woff2", f"{VENDOR_DIR}/katex/fonts/KaTeX_Math-Italic.woff2"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/fonts/KaTeX_Size1-Regular.woff2", f"{VENDOR_DIR}/katex/fonts/KaTeX_Size1-Regular.woff2"),
    ("https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/fonts/KaTeX_Size2-Regular.woff2", f"{VENDOR_DIR}/katex/fonts/KaTeX_Size2-Regular.woff2"),
    
    # Prism
    ("https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css", f"{VENDOR_DIR}/prism/prism-tomorrow.min.css"),
    ("https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js", f"{VENDOR_DIR}/prism/prism.min.js"),
    ("https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js", f"{VENDOR_DIR}/prism/prism-python.min.js"),
    ("https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-sql.min.js", f"{VENDOR_DIR}/prism/prism-sql.min.js"),

    # Marked & Extension
    ("https://cdnjs.cloudflare.com/ajax/libs/marked/15.0.7/marked.min.js", f"{VENDOR_DIR}/marked/marked.min.js"),
    ("https://cdn.jsdelivr.net/npm/marked-katex-extension@5.1.13/lib/index.umd.js", f"{VENDOR_DIR}/marked/marked-katex-extension.umd.js"),

    # Lucide
    ("https://unpkg.com/lucide@latest/dist/umd/lucide.js", f"{VENDOR_DIR}/lucide/lucide.min.js"),
]

for url, dest in files:
    try:
        print(f"Downloading {url} -> {dest}")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(dest, 'wb') as out_file:
            out_file.write(resp.read())
    except Exception as e:
        print(f"Warning downloading {url}: {e}")

print("Vendor download complete!")
