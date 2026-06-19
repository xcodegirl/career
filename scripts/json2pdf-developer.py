"""
Generate developer-style PDF resume from JSON source using LaTeX.
Calls json2tex-developer.py to generate LaTeX, then compiles with pdflatex.
Usage: python json2pdf-developer.py input.json [output.pdf]
"""
import os
import sys
import subprocess
import shutil


# =====================================================================
# UTILITY FUNCTIONS
# =====================================================================

def find_pdflatex():
    """Locate pdflatex executable on PATH."""
    pdflatex_path = shutil.which('pdflatex')
    if not pdflatex_path:
        raise FileNotFoundError(
            'pdflatex not found on PATH. Install MiKTeX or add its bin folder to PATH.'
        )
    return pdflatex_path


def compile_latex_to_pdf(tex_file, pdf_file, scripts_dir):
    """Compile LaTeX source to PDF using pdflatex."""
    temp_dir = os.path.dirname(tex_file)
    tex_basename = os.path.basename(tex_file)
    job_name = os.path.splitext(tex_basename)[0]

    print(f"Generated LaTeX: {tex_file}")

    pdflatex_cmd = find_pdflatex()

    # Set up environment: tell pdflatex where to find custom classes.
    original_texinputs = os.environ.get('TEXINPUTS', '')
    os.environ['TEXINPUTS'] = f'{scripts_dir};'

    try:
        result = subprocess.run(
            [pdflatex_cmd, '-interaction=nonstopmode', '-jobname', job_name,
             '-output-directory', temp_dir, tex_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            print("pdflatex output:", result.stdout)
            print("pdflatex errors:", result.stderr)
            raise RuntimeError(f'PDF compilation failed with exit code {result.returncode}')

        # Clean up temporary LaTeX build artifacts.
        for suffix in ['aux', 'log', 'out']:
            aux_file = os.path.join(temp_dir, f'{job_name}.{suffix}')
            if os.path.exists(aux_file):
                os.remove(aux_file)

        print(f"Generated PDF: {pdf_file}")

    finally:
        os.environ['TEXINPUTS'] = original_texinputs


def generate_latex(json_path, tex_path, scripts_dir):
    """Call json2tex-developer.py to generate LaTeX from JSON."""
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(scripts_dir, 'json2tex-developer.py'), json_path, tex_path],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            print(f"Error generating LaTeX: {result.stderr}")
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_output_path(json_path, output_arg):
    """Determine output PDF path: use provided arg or derive from input."""
    if output_arg:
        return output_arg
    base_name = os.path.splitext(json_path)[0]
    return base_name + '-dev.pdf'


# =====================================================================
# MAIN ENTRY POINT
# =====================================================================

def main():
    if len(sys.argv) < 2:
        print("Usage: python json2pdf-developer.py input.json [output.pdf]")
        sys.exit(1)

    json_path = sys.argv[1]
    output_pdf = get_output_path(json_path, sys.argv[2] if len(sys.argv) > 2 else None)

    # Validate input file exists.
    if not os.path.exists(json_path):
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    scripts_dir = os.path.dirname(os.path.abspath(__file__))
    tex_path = os.path.splitext(output_pdf)[0] + '.tex'

    # Generate LaTeX source from JSON.
    generate_latex(json_path, tex_path, scripts_dir)

    # Compile LaTeX to PDF.
    try:
        compile_latex_to_pdf(tex_path, output_pdf, scripts_dir)
        print(f"\nSuccessfully generated CV (developer style): {output_pdf}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
