import json
import os
import sys


def txt_escape(text):
    """Normalize text for plain-text resume output."""
    if not isinstance(text, str):
        return text
    text = text.replace('’', "'").replace('‘', "'")
    text = text.replace('“', '"').replace('”', '"')
    text = text.replace('–', '-').replace('—', '--')
    return text


SECTION_WIDTH = 78


def add_section(lines, title):
    lines.append(title.upper())
    lines.append('-' * min(len(title), SECTION_WIDTH))



def main():
    # Usage: python json2txt.py input.json [output.txt]
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python json2txt.py input.json [output.txt]")
        sys.exit(1)
    if len(sys.argv) > 2:
        txt_file = sys.argv[2]
    else:
        txt_file = os.path.splitext(json_file)[0] + '.txt'

    with open(json_file, encoding='utf-8') as handle:
        data = json.load(handle)

    lines = []
    lines.append(txt_escape(data['name']))
    lines.append(txt_escape(data['title']))
    lines.append('')

    contact = data.get('contact', {})
    contact_lines = []
    if 'location' in contact:
        contact_lines.append(f"Location: {txt_escape(contact['location'])}")
    if 'phone' in contact:
        contact_lines.append(f"Phone: {txt_escape(contact['phone'])}")
    if 'email' in contact:
        contact_lines.append(f"Email: {txt_escape(contact['email'])}")
    if 'linkedin' in contact:
        contact_lines.append(f"LinkedIn: {txt_escape(contact['linkedin'])}")
    if 'github' in contact:
        contact_lines.append(f"GitHub: {txt_escape(contact['github'])}")
    if 'discord' in contact:
        contact_lines.append(f"Discord: {txt_escape(contact['discord'])}")
    if contact_lines:
        add_section(lines, 'Contact')
        lines.extend(contact_lines)
        lines.append('')

    if data.get('summary'):
        add_section(lines, 'Summary')
        lines.append(txt_escape(data['summary']))
        lines.append('')

    if data.get('experience'):
        add_section(lines, 'Experience')
        for exp in data['experience']:
            lines.append(f"{txt_escape(exp['title'])} | {txt_escape(exp['company'])}")
            lines.append(txt_escape(exp['date']))
            lines.append(txt_escape(exp['description']))
            techs = exp.get('technologies', [])
            if techs:
                lines.append('Technologies: ' + ', '.join(txt_escape(item) for item in techs))
            lines.append('')

    if data.get('education'):
        add_section(lines, 'Education')
        for edu in data['education']:
            lines.append(f"{txt_escape(edu.get('degree', ''))} | {txt_escape(edu.get('institution', ''))}")
            if edu.get('date'):
                lines.append(txt_escape(edu['date']))
            if edu.get('field'):
                lines.append(f"Field: {txt_escape(edu['field'])}")
            if edu.get('thesis'):
                lines.append(f"Thesis: {txt_escape(edu['thesis'])}")
            lines.append('')

    if data.get('community_outreach'):
        add_section(lines, 'Community Outreach')
        for item in data['community_outreach']:
            org = f", {txt_escape(item['organization'])}" if item.get('organization') else ''
            lines.append(f"- {txt_escape(item['role'])}{org} ({txt_escape(item['years'])})")
        lines.append('')

    if data.get('awards'):
        add_section(lines, 'Awards')
        for award in data['awards']:
            parts = [txt_escape(award['title'])]
            if award.get('organization'):
                parts.append(txt_escape(award['organization']))
            if award.get('year'):
                parts.append(txt_escape(award['year']))
            lines.append('- ' + ', '.join(parts))
        lines.append('')

    if data.get('languages'):
        add_section(lines, 'Languages')
        for language in data['languages']:
            lines.append(f"- {txt_escape(language['language'])}: {txt_escape(language['proficiency'])}")
        lines.append('')

    if data.get('portfolio'):
        add_section(lines, 'Portfolio')
        for sample in data['portfolio']:
            lines.append(f"- {txt_escape(sample['title'])}: {txt_escape(sample['url'])}")
        lines.append('')

    if data.get('published_games'):
        add_section(lines, 'Published Games')
        for game in data['published_games']:
            platforms = ', '.join(txt_escape(platform) for platform in game['platforms'])
            year = game['year'] if isinstance(game['year'], str) else ', '.join(txt_escape(item) for item in game['year'])
            lines.append(f"- {txt_escape(game['title'])} ({platforms}; {txt_escape(year)})")
        lines.append('')

    if os.path.exists(txt_file):
        print(f"Overwriting existing file: {txt_file}")

    with open(txt_file, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines).rstrip() + '\n')

    print(f"Wrote plain-text resume to: {txt_file}")


if __name__ == '__main__':
    main()
