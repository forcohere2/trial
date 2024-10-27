import os
import subprocess
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import ocrmypdf
import fitz  # PyMuPDF
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['OUTPUT_FOLDER'] = "outputs"

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed extensions for document upload
ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_docx_text_extraction(pdf_path, docx_path):
    # Initialize a new DOCX document
    doc = Document()
    with fitz.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf):
            text = page.get_text("text")  # Extract searchable text
            if text.strip():  # Ensure there's text to add
                doc.add_paragraph(f"Page {page_num + 1}\n{text}")
    doc.save(docx_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    document = request.files['file']
    filename = secure_filename(document.filename)

    # Ensure the uploaded file is allowed
    if not allowed_file(filename):
        return jsonify({"error": f"Only {', '.join(ALLOWED_EXTENSIONS)} files are allowed."}), 400

    # Save the uploaded file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    document.save(file_path)

    # Check OCR options from form data
    ocr_enabled = request.form.get('ocrCheckbox') == 'on'
    selected_languages = []
    if request.form.get('lang-eng'):
        selected_languages.append('eng')
    if request.form.get('lang-guj'):
        selected_languages.append('guj')
    if request.form.get('lang-san'):
        selected_languages.append('san')
    if request.form.get('lang-hin'):
        selected_languages.append('hin')
    languages = '+'.join(selected_languages) if selected_languages else 'eng'

    # Convert .doc and .pdf to .docx if needed
    if filename.endswith('.doc') or filename.endswith('.pdf'):
        docx_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename.rsplit('.', 1)[0] + '.docx')

        try:
            if filename.endswith('.doc'):
                # Convert .doc to .docx using LibreOffice
                convert_command = [
                    'libreoffice',
                    '--headless',
                    '--convert-to', 'docx',
                    '--outdir', app.config['UPLOAD_FOLDER'],
                    file_path
                ]
                subprocess.run(convert_command, check=True)
            elif filename.endswith('.pdf'):
                # Only apply OCR if the checkbox is checked
                if ocr_enabled:
                    try:
                        # Perform OCR on the PDF and overwrite with a searchable version
                        ocrmypdf.ocr(file_path, file_path, language=languages, force_ocr=True, output_type='pdf')
                    except Exception as ocr_error:
                        return jsonify({"error": f"Error making PDF searchable: {str(ocr_error)}"}), 500
                    # Convert PDF to DOCX using text extraction to ensure searchability
                    pdf_to_docx_text_extraction(file_path, docx_file_path)
                else:
                    # Convert PDF to DOCX using pdf2docx with layout preservation for tables
                    cv = Converter(file_path)
                    cv.convert(docx_file_path, start=0, end=None, layout='exact')  # Preserve layout better
                    cv.close()
            # Use the converted .docx file for further processing
            file_path = docx_file_path
        except Exception as e:
            return jsonify({"error": f"Error converting to .docx: {str(e)}"}), 500

    # Convert .docx file to .html
    output_html = os.path.join(app.config['OUTPUT_FOLDER'], filename.rsplit('.', 1)[0] + '.html')

    try:
        # Try using LibreOffice for conversion
        convert_command = [
            'libreoffice',
            '--headless',
            '--convert-to', 'html',
            '--outdir', app.config['OUTPUT_FOLDER'],
            file_path
        ]
        subprocess.run(convert_command, check=True)
    except subprocess.CalledProcessError:
        # Fallback to Pandoc if LibreOffice fails
        try:
            convert_command = ['pandoc', file_path, '-o', output_html]
            subprocess.run(convert_command, check=True)
        except Exception as e:
            return jsonify({"error": f"Error converting document to HTML: {str(e)}"}), 500

    # Return the HTML URL for display in the viewer
    return jsonify({"html_url": f"/outputs/{filename.rsplit('.', 1)[0]}.html"})

# Serve the converted HTML file
@app.route('/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')