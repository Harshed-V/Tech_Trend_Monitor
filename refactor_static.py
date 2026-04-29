import os
import re

base_html_path = 'templates/base.html'
index_html_path = 'templates/index.html'

os.makedirs('static/css', exist_ok=True)
os.makedirs('static/js', exist_ok=True)

with open(base_html_path, 'r', encoding='utf-8') as f:
    base_content = f.read()

with open(index_html_path, 'r', encoding='utf-8') as f:
    index_content = f.read()

# Extract CSS from base.html
style_match = re.search(r'<style>(.*?)</style>', base_content, re.DOTALL)
if style_match:
    css_content = style_match.group(1).strip()
    with open('static/css/style.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    # Replace in base.html
    base_content = base_content.replace(style_match.group(0), '<link rel="stylesheet" href="{{ url_for(\'static\', filename=\'css/style.css\') }}">')

# Extract JS from base.html
script_match = re.search(r'<script>(.*?)</script>', base_content, re.DOTALL)
js_base_content = ''
if script_match:
    js_base_content = script_match.group(1).strip()
    # Remove from base.html
    base_content = base_content.replace(script_match.group(0), '')

# Add main.js link in base.html right before </body>
base_content = base_content.replace('</body>', '<script src="{{ url_for(\'static\', filename=\'js/main.js\') }}" defer></script>\n</body>')

# Extract JS from index.html
script_match_index = re.search(r'<script>(.*?)</script>', index_content, re.DOTALL)
js_index_content = ''
if script_match_index:
    js_index_content = script_match_index.group(1).strip()
    # Replace in index.html with APP_CONFIG
    config_script = '''<script>
    window.APP_CONFIG = {
        selectedType: "{{ selected_type }}"
    };
</script>'''
    index_content = index_content.replace(script_match_index.group(0), config_script)

# Combine JS and update selectedType reference in js_index_content
# Change: const selectedType = "{{ selected_type }}"; -> const selectedType = window.APP_CONFIG ? window.APP_CONFIG.selectedType : 'weekly';
js_index_content = re.sub(r'const selectedType = "{{ selected_type }}";', 'const selectedType = window.APP_CONFIG ? window.APP_CONFIG.selectedType : \'weekly\';', js_index_content)

combined_js = js_base_content + '\n\n' + js_index_content
with open('static/js/main.js', 'w', encoding='utf-8') as f:
    f.write(combined_js)

with open(base_html_path, 'w', encoding='utf-8') as f:
    f.write(base_content)

with open(index_html_path, 'w', encoding='utf-8') as f:
    f.write(index_content)

print('Refactoring complete')
