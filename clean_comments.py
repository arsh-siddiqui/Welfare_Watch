import os, re, glob, codecs

def clean_python_comments(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f: content = f.read()
    # Simplify large comment banners: '# ── Title ──' -> '# Title'
    content = re.sub(r'#\s*[-=═─]+([^-=═─\n]*?)[-=═─]+\s*\n', lambda m: f"# {m.group(1).strip()}\n" if m.group(1).strip() else "", content)
    with codecs.open(filepath, 'w', 'utf-8') as f: f.write(content)

def clean_css_comments(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f: content = f.read()
    def simplify_match(m):
        inner = m.group(1).strip()
        return f"/* {inner} */" if inner else ""
    content = re.sub(r'/\*[\s*═─]+([^*]*?)[\s*═─]+\*/', simplify_match, content)
    content = re.sub(r'/\*\s*\*/\n?', '', content)
    with codecs.open(filepath, 'w', 'utf-8') as f: f.write(content)

def clean_html_comments(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f: content = f.read()
    def html_match(m):
        inner = m.group(0)
        return inner if '{{' in inner or '{%' in inner else ""
    content = re.sub(r'<!--.*?-->', html_match, content, flags=re.DOTALL)
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    with codecs.open(filepath, 'w', 'utf-8') as f: f.write(content)

if __name__ == '__main__':
    base_dir = r'c:\Users\Arsh\Downloads\WelfareWatch-main\WelfareWatch-main'
    for py_file in glob.glob(os.path.join(base_dir, '*.py')):
        if py_file.endswith('clean_comments.py'): continue
        clean_python_comments(py_file)
    for css_file in glob.glob(os.path.join(base_dir, 'static', 'css', '*.css')):
        clean_css_comments(css_file)
    for html_file in glob.glob(os.path.join(base_dir, 'templates', '*.html')):
        clean_html_comments(html_file)
    print("Comment cleanup complete.")
