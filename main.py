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
def modify_newsletter_html(html_content, filename):
    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. Set the title to the filename without extension
    filename_without_ext = os.path.splitext(filename)[0]
    if soup.title:
        soup.title.string = filename_without_ext
    else:
        # Create title tag if it doesn't exist
        title_tag = soup.new_tag('title')
        title_tag.string = filename_without_ext
        if soup.head:
            soup.head.append(title_tag)
        else:
            # Create head if it doesn't exist
            head_tag = soup.new_tag('head')
            head_tag.append(title_tag)
            if soup.html:
                soup.html.insert(0, head_tag)
            else:
                soup.insert(0, head_tag)

    # 2. Add logo with link to index.html at the top left (keeping aspect ratio)
    logo_html = '''
    <div style="position: fixed; top: 10px; left: 10px; z-index: 9999;">
        <a href="../index.html" style="text-decoration: none; display: inline-block;">
            <img src="../logo.png" alt="Logo" style="width: 120px; height: auto; max-height: 120px;">
        </a>
    </div>
    '''

    # 3. Add secret.png at bottom left of entire page (not fixed position)
    secret_html = '''
    <div style="position: absolute; bottom: 10px; left: 10px; z-index: 9999; pointer-events: none;">
        <img src="secret.png" alt="Secret" style="width: 60px; height: 60px; object-fit: contain;">
    </div>
    '''

    # Add the logo to the body
    if soup.body:
        soup.body.insert(0, BeautifulSoup(logo_html, 'html.parser'))
        # Add secret.png at the end of body
        soup.body.append(BeautifulSoup(secret_html, 'html.parser'))
        # Make body relative so absolute positioning works for secret image
        if soup.body.has_attr('style'):
            current_style = soup.body['style']
            if 'position:' not in current_style:
                soup.body['style'] = current_style + ' position: relative !important;'
        else:
            soup.body['style'] = 'position: relative !important;'

    # 4. Black background body
    body = soup.find('body')
    if body:
        # Add to existing style or create new
        if body.has_attr('style'):
            current_style = body['style']
            if 'background-color' not in current_style:
                body['style'] = current_style + ' background-color: black !important;'
            if 'margin' not in current_style:
                body['style'] = body['style'] + ' margin: 0 !important;'
            if 'padding' not in current_style:
                body['style'] = body['style'] + ' padding: 0 !important;'
        else:
            body['style'] = 'background-color: black !important; margin: 0 !important; padding: 0 !important; position: relative !important;'

    # 5. Top-level .pdf24_02 divs
    top_divs = soup.find_all('div', class_='pdf24_ pdf24_02')
    for div in top_divs:
        if div.has_attr('style'):
            del div['style']
        div['style'] = 'margin: 0 auto !important; background-color: black !important; position: relative !important; display: block !important; box-shadow: none !important;'

    # 6. Clean existing styles
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

    # 7. Global centering
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

    # 8. Remove spacing on .pdf24_06
    for div in soup.find_all('div', class_='pdf24_06'):
        if div.has_attr('style'):
            current_style = div['style']
            current_style = re.sub(r'height\s*:\s*[^;]+;?', '', current_style)
            div['style'] = current_style

    return str(soup)

# === PROCESS AND SAVE MODIFIED NEWSLETTERS ===
# Get all HTML files with their modification times
newsletter_files_with_time = []
for f in os.listdir(html_folder):
    if f.lower().endswith(".html"):
        file_path = os.path.join(html_folder, f)
        mod_time = os.path.getmtime(file_path)  # Get modification time
        newsletter_files_with_time.append((mod_time, f))

# Sort by modification time (newest first, oldest last)
newsletter_files_with_time.sort(reverse=True)  # reverse=True puts newest first
newsletter_files = [f for mod_time, f in newsletter_files_with_time]

modified_files = []

for file in newsletter_files:
    src_path = os.path.join(html_folder, file)
    dst_path = os.path.join(modified_folder, file)

    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified_content = modify_newsletter_html(content, file)

    with open(dst_path, 'w', encoding='utf-8') as f:
        f.write(modified_content)

    modified_files.append(file)

print(f"Modified {len(modified_files)} newsletters into '{modified_folder}' (sorted newest first).")

# === GENERATE MAIN INDEX.HTML ===
html_menu_items = [f'<li><a href="{modified_folder}/{f}">* {os.path.splitext(f)[0]}</a></li>' for f in modified_files]

# Add logo to index.html as well (top-left)
logo_for_index = '''
<div style="position: fixed; top: 10px; left: 10px; z-index: 9999;">
    <a href="index.html" style="text-decoration: none; display: inline-block;">
        <img src="logo.png" alt="Logo" style="width: 120px; height: auto; max-height: 120px;">
    </a>
</div>
'''

# Add background music to index.html only (plays at 50% volume, loops)
bg_music_html = '''
<audio id="bg-music" loop style="display: none;">
    <source src="bg.mp3" type="audio/mpeg">
</audio>
<script>
    document.addEventListener('DOMContentLoaded', function() {
        var bgMusic = document.getElementById('bg-music');
        if (bgMusic) {
            bgMusic.volume = 0.5; // Set to 50% volume
            // Try to play and handle autoplay restrictions
            bgMusic.play().catch(function(error) {
                console.log("Autoplay was prevented:", error);
                // Create a user interaction handler to start music
                function startMusicOnInteraction() {
                    bgMusic.play().then(function() {
                        console.log("Music started after user interaction");
                    }).catch(function(e) {
                        console.log("Still couldn't play:", e);
                    });
                    // Remove event listeners after first interaction
                    document.removeEventListener('click', startMusicOnInteraction);
                    document.removeEventListener('keydown', startMusicOnInteraction);
                    document.removeEventListener('touchstart', startMusicOnInteraction);
                }
                // Wait for user interaction
                document.addEventListener('click', startMusicOnInteraction);
                document.addEventListener('keydown', startMusicOnInteraction);
                document.addEventListener('touchstart', startMusicOnInteraction);
            });
        }
    });
</script>
'''

# JavaScript for random header color and text (1% chance)
header_randomizer_js = '''
<script>
document.addEventListener('DOMContentLoaded', function() {
    var header = document.querySelector('.header');
    if (header) {
        // 1% chance for purple header and "Welcome!" text
        if (Math.random() < 0.01) {
            header.style.color = '#800080';
            header.textContent = 'Welcome!';
        }
        // Otherwise it stays yellow with the default text
    }
});
</script>
'''

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
  color: yellow;
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
{logo_for_index}
{bg_music_html}
{header_randomizer_js}
<div class="box">
    <div class="header">Welcome to the Partymax Newsletter Archive!</div>
    <ul>
        {"".join(html_menu_items)}
    </ul>
</div>
</body>
</html>
"""

with open("index.html", 'w', encoding='utf-8') as f:
    f.write(html_index)

print("Generated index.html with JavaScript random header (1% chance for purple 'Welcome!')")

# === COPY FILES TO MODIFIED FOLDER FOR REFERENCE ===
logo_file = "logo.png"
if os.path.exists(logo_file):
    shutil.copy(logo_file, modified_folder)
    print(f"Copied {logo_file} to {modified_folder}/ for reference")
else:
    print(f"Warning: {logo_file} not found. Please create a logo.png file in the main directory.")

# Check and copy secret.png to modified folder
secret_file = "secret.png"
if os.path.exists(secret_file):
    shutil.copy(secret_file, modified_folder)
    print(f"Copied {secret_file} to {modified_folder}/ for newsletter pages")
else:
    print(f"Warning: {secret_file} not found. The secret image won't appear on newsletter pages.")

# Check if bg.mp3 exists and warn if not
bg_music_file = "bg.mp3"
if not os.path.exists(bg_music_file):
    print(f"Warning: {bg_music_file} not found. Background music will not play.")
else:
    # Copy bg.mp3 to modified folder for consistency (though only index.html uses it)
    shutil.copy(bg_music_file, modified_folder)
    print(f"Copied {bg_music_file} to {modified_folder}/ for reference")