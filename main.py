import os
from bs4 import BeautifulSoup
import re
import shutil

# === CONFIG ===
html_folder = "newsletters"   # folder with newsletter HTML files
modified_folder = "newsletters_modified"  # output for auto-fixed HTMLs
os.makedirs(html_folder, exist_ok=True)
os.makedirs(modified_folder, exist_ok=True)

# === FUNCTION TO MODIFY NEWSLETTER HTML ===
def modify_newsletter_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Black background body
    body = soup.find('body')
    if body:
        body['style'] = 'background-color: black !important; margin: 0 !important; padding: 0 !important;'

    # 2. Top-level .pdf24_02 divs
    top_divs = soup.find_all('div', class_='pdf24_ pdf24_02')
    for div in top_divs:
        if div.has_attr('style'):
            del div['style']
        div['style'] = 'margin: 0 auto !important; background-color: black !important; position: relative !important; display: block !important; box-shadow: none !important;'

    # 3. Clean existing styles
    style_tags = soup.find_all('style')
    for style_tag in style_tags:
        css_content = style_tag.string
        if css_content:
            css_content = re.sub(
                r'body > div \{.*?\}',
                'body > div {\n\tbox-shadow: none !important;\n\tmargin: 0 !important;\n\tpadding: 0 !important;\n}',
                css_content,
                flags=re.DOTALL
            )
            css_content = css_content.replace('@media print', '')
            css_content = css_content.replace('.pdf24_06', '.pdf24_06 { height: auto !important; }')
            style_tag.string = css_content

    # 4. Global centering
    global_style = """
    <style>
        body, html {
            background-color: black !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            flex-direction: column !important;
            align-items: center !important;
            justify-content: center !important;
            min-height: 100vh !important;
            width: 100% !important;
        }

        .pdf24_02 {
            background-color: black !important;
            margin: 0 auto !important;
            padding: 0 !important;
            display: block !important;
            box-shadow: none !important;
            position: relative !important;
        }

        .pdf24_view {
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            width: 100% !important;
        }

        .pdf24_05 {
            margin: 0 auto !important;
        }

        /* Remove all gaps between pages */
        .pdf24_ + .pdf24_ {
            margin-top: 0 !important;
        }
    </style>
    """
    head = soup.find('head')
    if head:
        head.append(BeautifulSoup(global_style, 'html.parser'))

    # 5. Remove spacing on .pdf24_06
    for div in soup.find_all('div', class_='pdf24_06'):
        if div.has_attr('style'):
            current_style = div['style']
            current_style = re.sub(r'height\s*:\s*[^;]+;?', '', current_style)
            div['style'] = current_style

    return str(soup)

# === PROCESS AND SAVE MODIFIED NEWSLETTERS ===
newsletter_files = sorted(f for f in os.listdir(html_folder) if f.lower().endswith(".html"))
modified_files = []

for file in newsletter_files:
    src_path = os.path.join(html_folder, file)
    dst_path = os.path.join(modified_folder, file)

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified_content = modify_newsletter_html(content)

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    modified_files.append(file)

print(f"Modified {len(modified_files)} newsletters into '{modified_folder}'.")

# === GENERATE MAIN INDEX.HTML ===
html_menu_items = [f'<li><a href="{modified_folder}/{f}">* {f[:-5]}</a></li>' for f in modified_files]

html_index = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>* Newsletters</title>
<style>
@font-face {{
  font-family: "Determination";
  src: url("determination.ttf") format("truetype");
}}

html, body {{
  margin:0; padding:0;
  width:100%; height:100%;
  background:black; color:white;
  font-family:"Determination", monospace;
  display:flex;
  align-items:center;
  justify-content:center;
}}

.box {{
  padding:32px;
  border:2px solid white;
  min-width:360px;
  display:flex;
  flex-direction:column;
  justify-content:center;
  align-items:center;
}}

.header {{
  font-size:32px;
  margin-bottom:24px;
  color: cyan;
}}

ul {{
  list-style:none;
  padding:0;
  margin:0;
  text-align:center;
}}

li {{
  margin:14px 0;
}}

a {{
  color:white;
  text-decoration:none;
  font-size:26px;
  display:inline-block;
}}

a:hover {{
  color:yellow;
}}
</style>
</head>
<body>
<div class="box">
    <div class="header">Welcome to the Newsletter Archive!</div>
    <ul>
        {"".join(html_menu_items)}
    </ul>
</div>
</body>
</html>
"""

with open("index.html", 'w', encoding='utf-8') as f:
    f.write(html_index)

print("Generated index.html with links to all modified newsletters.")


html_files = sorted(f for f in os.listdir(modified_folder) if f.lower().endswith(".html"))

# generate menu items
html_menu_items = [f'<li><a href="{modified_folder}/{f}">* {f[:-5]}</a></li>' for f in html_files]

# generate main index.html
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>* Newsletters</title>
<style>
@font-face {{
  font-family: "Determination";
  src: url("determination.ttf") format("truetype");
}}

html, body {{
  margin:0; padding:0;
  width:100%; height:100%;
  background:black; color:white;
  font-family:"Determination", monospace;
}}

body {{
  display:flex;
  align-items:center;
  justify-content:center;
  text-align:center;
}}

.box {{
  padding:32px;
  border:2px solid white;
  min-width:360px;
}}

ul {{list-style:none; padding:0; margin:0;}}
li {{margin:14px 0;}}
a {{color:white; text-decoration:none; font-size:26px;}}
a:hover {{color:yellow;}}

.header {{
  font-size:32px;
  margin-bottom:24px;
  color:cyan;
}}
</style>
</head>
<body>
<div class="box">
  <div class="header">Welcome to the Newsletter Archive!</div>
  <ul>
    """ + "\n".join(html_menu_items) + """
  </ul>
</div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"Generated index.html with {len(html_files)} newsletters.")
