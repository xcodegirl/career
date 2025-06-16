import json
import sys

def html_escape(text):
    """Escape HTML special characters and normalize quotes/dashes."""
    if not isinstance(text, str):
        return text
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    text = text.replace('"', '&quot;').replace("'", '&#39;')
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('–', '-').replace('—', '--')
    return text

def main():
    # Usage: python json2html.py input.json [output.html]
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python json2html.py input.json [output.html]")
        sys.exit(1)
    if len(sys.argv) > 2:
        html_file = sys.argv[2]
    else:
        html_file = json_file.replace('.json', '-resume.html')

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    lines = []
    lines.append('<!DOCTYPE html>')
    lines.append('<html lang="en">')
    lines.append('<head>')
    lines.append('<meta charset="UTF-8">')
    lines.append(f'<title>{html_escape(data["name"])} - Resume</title>')
    lines.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    lines.append('<style>')
    lines.append('body {'
                 '  font-family: "Segoe UI", Arial, sans-serif;'
                 '  background: linear-gradient(120deg, #e0e7ff 0%, #f8fafc 100%);'
                 '  color: #232946;'
                 '  margin: 0;'
                 '  min-height: 100vh;'
                 '}')
    lines.append('.container {'
                 '  max-width: 800px;'
                 '  margin: 48px auto 48px auto;'
                 '  background: #fff;'
                 '  border-radius: 18px;'
                 '  box-shadow: 0 8px 32px rgba(44,62,80,0.10);'
                 '  padding: 48px 32px 40px 32px;'
                 '  border: 1px solid #e0e0e0;'
                 '}')
    lines.append('h1 { font-size: 2.7em; margin-bottom: 0.1em; letter-spacing: 1px; color: #232946; }')
    lines.append('h2 { border-bottom: 2px solid #e0e7ff; padding-bottom: 0.2em; margin-top: 2em; color: #3d5af1; font-size: 1.3em; }')
    lines.append('h3 { margin-bottom: 0.2em; margin-top: 1.2em; font-size: 1.1em; color: #232946; }')
    lines.append('.contact-list { list-style: none; padding: 0; margin-bottom: 1.5em; }')
    lines.append('.contact-list li { display: inline-block; margin-right: 1.5em; color: #555; font-size: 1em; }')
    lines.append('ul { margin-top: 0.3em; margin-bottom: 1em; }')
    lines.append('li { margin-bottom: 0.2em; }')
    lines.append('.section { margin-bottom: 2em; }')
    lines.append('code { background: #f3f3f3; border-radius: 3px; padding: 2px 5px; font-size: 0.97em; }')
    lines.append('em { color: #666; }')
    lines.append('a { color: #3d5af1; text-decoration: none; border-bottom: 1px dotted #3d5af1; transition: color 0.2s, border-bottom 0.2s; }')
    lines.append('a:hover { color: #232946; border-bottom: 1px solid #232946; }')
    lines.append('@media (max-width: 600px) {'
                 '  .container { padding: 18px 4vw 18px 4vw; }'
                 '  h1 { font-size: 2em; }'
                 '  h2 { font-size: 1.1em; }'
                 '}')
    lines.append('</style>')
    lines.append('</head>')
    lines.append('<body>')
    lines.append('<div class="container">')

    # Header
    lines.append(f'<h1>{html_escape(data["name"])}</h1>')
    lines.append(f'<div style="font-size:1.2em; color:#444; margin-bottom:0.7em;">{html_escape(data["title"])}</div>')

    # Contact
    contact = data.get('contact', {})
    contact_items = []
    if "location" in contact:
        contact_items.append(f'<li>📍 {html_escape(contact["location"])}</li>')
    if "phone" in contact:
        contact_items.append(f'<li>📞 {html_escape(contact["phone"])}</li>')
    if "email" in contact:
        contact_items.append(f'<li>✉️ <a href="mailto:{html_escape(contact["email"])}">{html_escape(contact["email"])}</a></li>')
    if "linkedin" in contact:
        contact_items.append(f'<li><a href="{html_escape(contact["linkedin"])}">LinkedIn</a></li>')
    if "github" in contact:
        contact_items.append(f'<li><a href="{html_escape(contact["github"])}">GitHub</a></li>')
    if "discord" in contact:
        contact_items.append(f'<li>Discord: <code>{html_escape(contact["discord"])}</code></li>')
    if contact_items:
        lines.append('<ul class="contact-list">')
        lines.extend(contact_items)
        lines.append('</ul>')

    # Summary
    if data.get("summary"):
        lines.append('<div class="section">')
        lines.append('<h2>Summary</h2>')
        lines.append(f'<p>{html_escape(data["summary"])}</p>')
        lines.append('</div>')

    # Experience
    if data.get("experience"):
        lines.append('<div class="section">')
        lines.append('<h2>Experience</h2>')
        for exp in data["experience"]:
            lines.append(f'<h3>{html_escape(exp["title"])} <span style="font-weight:normal;">- {html_escape(exp["company"])}</span></h3>')
            lines.append(f'<div><em>{html_escape(exp["date"])}</em></div>')
            lines.append(f'<ul><li>{html_escape(exp["description"])}</li>')
            techs = exp.get("technologies", [])
            if techs:
                lines.append(f'<li><strong>Technologies:</strong> {", ".join(html_escape(t) for t in techs)}</li>')
            lines.append('</ul>')
        lines.append('</div>')

    # Education
    if data.get("education"):
        lines.append('<div class="section">')
        lines.append('<h2>Education</h2>')
        for edu in data["education"]:
            lines.append(f'<h3>{html_escape(edu["degree"])} - {html_escape(edu["institution"])}</h3>')
            lines.append(f'<div><em>{html_escape(edu["date"])}</em></div>')
            lines.append(f'<div>Field: {html_escape(edu["field"])}</div>')
            if edu.get("thesis"):
                lines.append(f'<div>Thesis: <em>{html_escape(edu["thesis"])}</em></div>')
        lines.append('</div>')

    # Community Outreach
    if data.get("community_outreach"):
        lines.append('<div class="section">')
        lines.append('<h2>Community Outreach</h2>')
        lines.append('<ul>')
        for c in data["community_outreach"]:
            org = f", {html_escape(c['organization'])}" if c.get("organization") else ""
            lines.append(f'<li><strong>{html_escape(c["role"])}</strong>{org} ({html_escape(c["years"])})</li>')
        lines.append('</ul>')
        lines.append('</div>')

    # Awards
    if data.get("awards"):
        lines.append('<div class="section">')
        lines.append('<h2>Awards</h2>')
        lines.append('<ul>')
        for a in data["awards"]:
            org = f", {html_escape(a['organization'])}" if a.get("organization") else ""
            year = f", {html_escape(a['year'])}" if a.get("year") else ""
            lines.append(f'<li>{html_escape(a["title"])}{org}{year}</li>')
        lines.append('</ul>')
        lines.append('</div>')

    # Languages
    if data.get("languages"):
        lines.append('<div class="section">')
        lines.append('<h2>Languages</h2>')
        lines.append('<ul>')
        for l in data["languages"]:
            lines.append(f'<li>{html_escape(l["language"])}: {html_escape(l["proficiency"])}</li>')
        lines.append('</ul>')
        lines.append('</div>')

    # Work Samples
    if data.get("work_samples"):
        lines.append('<div class="section">')
        lines.append('<h2>Work Samples</h2>')
        lines.append('<ul>')
        for ws in data["work_samples"]:
            lines.append(f'<li><a href="{html_escape(ws["url"])}">{html_escape(ws["title"])}</a></li>')
        lines.append('</ul>')
        lines.append('</div>')

    # Published Games
    if data.get("published_games"):
        lines.append('<div class="section">')
        lines.append('<h2>Published Games</h2>')
        lines.append('<ul>')
        for g in data["published_games"]:
            platforms = ', '.join(html_escape(p) for p in g["platforms"])
            year = g["year"] if isinstance(g["year"], str) else ', '.join(html_escape(y) for y in g["year"])
            lines.append(f'<li><strong>{html_escape(g["title"])}</strong> ({platforms}, {html_escape(year)})</li>')
        lines.append('</ul>')
        lines.append('</div>')

    lines.append('</div>')
    lines.append('</body>')
    lines.append('</html>')

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

if __name__ == "__main__":
    main()