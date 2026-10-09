import os
import re
import urllib.parse

def convert_to_utf8(filepath):
    try:
        with open(filepath, 'rb') as f:
            raw = f.read()
    except Exception:
        return

    decoded = None
    for enc in ['windows-1251', 'cp866', 'koi8-r']:
        try:
            decoded = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if decoded is None:
        try:
            decoded = raw.decode('utf-8')
        except UnicodeDecodeError:
            return

    if re.search(r'<meta[^>]*charset=[^>]*>', decoded, re.IGNORECASE):
        decoded = re.sub(r'<meta[^>]*charset=["\']?[^"\'>\s]+["\']?[^>]*>', '<meta charset="utf-8">', decoded, flags=re.IGNORECASE)
    elif '<head>' in decoded.lower():
        decoded = re.sub(r'(<head[^>]*>)', r'\1\n<meta charset="utf-8">', decoded, count=1, flags=re.IGNORECASE)
    else:
        decoded = '<meta charset="utf-8">\n' + decoded

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(decoded)

def run():
    ignore = {'.git', '.github', '.nojekyll', 'fix.py', 'index.html'}
    
    print("1. Исправление кодировки всех HTML на UTF-8...")
    for root, dirs, files in os.walk('.'):
        if any(ig in root.split(os.sep) for ig in ['.git', '.github']):
            continue
        for f in files:
            if f.lower().endswith(('.htm', '.html', '.txt')):
                convert_to_utf8(os.path.join(root, f))

    print("2. Генерация каталога index.html...")
    html = [
        '<!doctype html>',
        '<html lang="ru">',
        '<head>',
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        '<title>Библиотека методических указаний</title>',
        '<style>',
        'body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; max-width: 960px; margin: 30px auto; padding: 0 20px; line-height: 1.5; background: #f8fafc; color: #0f172a; }',
        'h1 { font-size: 26px; border-bottom: 2px solid #cbd5e1; padding-bottom: 12px; margin-bottom: 24px; }',
        'details { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 12px; padding: 12px 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }',
        'summary { font-size: 18px; font-weight: 600; cursor: pointer; color: #0369a1; user-select: none; }',
        'summary:hover { color: #0284c7; }',
        'ul { list-style: none; padding-left: 10px; margin-top: 10px; }',
        'li { margin: 6px 0; }',
        'a { color: #2563eb; text-decoration: none; word-break: break-all; }',
        'a:hover { text-decoration: underline; color: #1d4ed8; }',
        '.badge { font-size: 11px; padding: 2px 6px; border-radius: 4px; font-weight: 600; margin-left: 6px; }',
        '.badge-start { background: #dcfce7; color: #15803d; }',
        '.badge-file { background: #f1f5f9; color: #475569; }',
        '</style>',
        '</head>',
        '<body>',
        '<h1>📚 Библиотека методических материалов</h1>',
        '<p>Нажмите на категорию, чтобы развернуть список документов:</p>'
    ]

    top_folders = sorted([d for d in os.listdir('.') if os.path.isdir(d) and d not in ignore])

    for folder in top_folders:
        html.append(f'<details open><summary>📁 {folder}</summary><ul>')
        all_docs = []
        for root, dirs, files in os.walk(folder):
            for f in sorted(files):
                if f.lower().endswith(('.htm', '.html', '.pdf', '.doc', '.docx')):
                    rel = os.path.join(root, f)
                    url = urllib.parse.quote(rel.replace('\\', '/'))
                    all_docs.append((f, rel, url))

        starts = [x for x in all_docs if x[0].lower().startswith(('start', 'index'))]
        others = [x for x in all_docs if not x[0].lower().startswith(('start', 'index'))]

        for name, rel, url in starts + others:
            is_start = name.lower().startswith(('start', 'index'))
            badge = '<span class="badge badge-start">🚀 Стартовая страница</span>' if is_start else f'<span class="badge badge-file">{name.split(".")[-1].upper()}</span>'
            html.append(f'<li><a href="./{url}" target="_blank">{rel}</a> {badge}</li>')

        if not all_docs:
            html.append('<li><em>Нет документов</em></li>')
        html.append('</ul></details>')

    html.append('</body></html>')

    with open('index.html', 'w', encoding='utf-8') as out:
        out.write('\n'.join(html))
    print("Готово!")

if __name__ == '__main__':
    run()
