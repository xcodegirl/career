import json
import os
import sys
from datetime import datetime

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches
    from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
except ImportError:
    print("Error: python-docx is required. Install with: pip install python-docx")
    sys.exit(1)

def main():
    # Usage: python json2docx.py input.json [output.docx]
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    else:
        print("Usage: python json2docx.py input.json [output.docx]")
        sys.exit(1)
    if len(sys.argv) > 2:
        docx_file = sys.argv[2]
    else:
        docx_file = os.path.splitext(json_file)[0] + '.docx'

    with open(json_file, encoding='utf-8') as f:
        data = json.load(f)

    doc = Document()

    # Title and contact
    title = doc.add_paragraph()
    title_run = title.add_run(data["name"])
    title_run.font.size = Pt(28)
    title_run.font.bold = True
    title_run.font.color.rgb = RGBColor(42, 77, 122)
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    subtitle = doc.add_paragraph(data.get("title", ""))
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subtitle_run = subtitle.runs[0]
    subtitle_run.font.size = Pt(14)
    subtitle_run.font.color.rgb = RGBColor(100, 100, 100)

    # Contact info
    contact = data.get("contact", {})
    if contact:
        contact_para = doc.add_paragraph()
        contact_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        contact_items = []
        if "linkedin" in contact:
            contact_items.append(contact["linkedin"].split("/")[-1])
        if "github" in contact:
            contact_items.append(contact["github"].split("/")[-1])
        contact_para.add_run(" | ".join(contact_items))
        contact_para.paragraph_format.space_before = Pt(6)
        contact_para.paragraph_format.space_after = Pt(12)

    # Summary
    if data.get("summary"):
        doc.add_heading("Who Am I?", level=2)
        doc.add_paragraph(data["summary"])

    # Experience
    if data.get("experience"):
        doc.add_heading("Experience", level=2)
        for exp in data["experience"]:
            # Job title and company
            job_para = doc.add_paragraph(style='List Bullet')
            title_run = job_para.add_run(f"{exp.get('title', '')} - {exp.get('company', '')}")
            title_run.bold = True
            title_run.font.size = Pt(11)

            # Date
            date_para = doc.add_paragraph(exp.get("date", ""), style='List Bullet 2')
            date_para.paragraph_format.left_indent = Inches(0.5)
            date_run = date_para.runs[0]
            date_run.font.italic = True
            date_run.font.size = Pt(10)
            date_run.font.color.rgb = RGBColor(100, 100, 100)

            # Description
            desc_para = doc.add_paragraph(exp.get("description", ""), style='List Bullet 2')
            desc_para.paragraph_format.left_indent = Inches(0.5)

            # Technologies
            if exp.get("technologies"):
                tech_para = doc.add_paragraph(style='List Bullet 2')
                tech_para.paragraph_format.left_indent = Inches(0.5)
                tech_run = tech_para.add_run("Technologies: ")
                tech_run.bold = True
                tech_para.add_run(", ".join(exp["technologies"]))

    # Education
    if data.get("education"):
        doc.add_heading("Education", level=2)
        for edu in data["education"]:
            edu_para = doc.add_paragraph(style='List Bullet')
            degree_run = edu_para.add_run(f"{edu.get('degree', '')}")
            degree_run.bold = True
            degree_run.font.size = Pt(11)
            edu_para.add_run(f" in {edu.get('field', '')}")

            inst_para = doc.add_paragraph(style='List Bullet 2')
            inst_para.paragraph_format.left_indent = Inches(0.5)
            inst_run = inst_para.add_run(edu.get('institution', ''))
            inst_run.italic = True

            date_para = doc.add_paragraph(edu.get('date', ''), style='List Bullet 2')
            date_para.paragraph_format.left_indent = Inches(0.5)
            date_run = date_para.runs[0]
            date_run.font.color.rgb = RGBColor(100, 100, 100)

    # Awards
    if data.get("awards"):
        doc.add_heading("Awards & Honors", level=2)
        for award in data["awards"]:
            award_para = doc.add_paragraph(style='List Bullet')
            award_run = award_para.add_run(award.get('title', ''))
            award_run.bold = True
            award_para.add_run(f" - {award.get('organization', '')} ({award.get('year', '')})")

    # Languages
    if data.get("languages"):
        doc.add_heading("Languages", level=2)
        for lang in data["languages"]:
            lang_para = doc.add_paragraph(style='List Bullet')
            lang_para.add_run(f"{lang.get('language', '')}: {lang.get('proficiency', '')}")

    # Portfolio
    if data.get("portfolio"):
        doc.add_heading("Portfolio", level=2)
        for item in data["portfolio"]:
            port_para = doc.add_paragraph(style='List Bullet')
            link_run = port_para.add_run(item.get('title', ''))
            link_run.font.color.rgb = RGBColor(61, 90, 241)
            link_run.underline = True
            port_para.add_run(f" - {item.get('url', '')}")

    # Published Games
    if data.get("published_games"):
        doc.add_heading("Published Games", level=2)
        for game in data["published_games"]:
            platforms = ', '.join(game["platforms"]) if isinstance(game["platforms"], list) else game["platforms"]
            year = game["year"] if isinstance(game["year"], str) else ', '.join(game["year"])
            game_para = doc.add_paragraph(style='List Bullet')
            game_run = game_para.add_run(game.get('title', ''))
            game_run.bold = True
            game_para.add_run(f" ({platforms}, {year})")

    if os.path.exists(docx_file):
        print(f"Overwriting existing file: {docx_file}")

    doc.save(docx_file)
    print(f"Wrote Word document to: {docx_file}")

if __name__ == "__main__":
    main()
