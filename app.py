import os
import subprocess
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import ocrmypdf

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
app.config['UPLOAD_FOLDER'] = "uploads"
app.config['OUTPUT_FOLDER'] = "outputs"

# Ensure the upload and output folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# Allowed extensions for document upload
ALLOWED_EXTENSIONS = {'docx', 'doc', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

    # Handle PDF conversion
    if filename.endswith('.pdf'):
        if ocr_enabled:
            try:
                # Perform OCR on the PDF to make it searchable
                ocrmypdf.ocr(file_path, file_path, language=languages, force_ocr=True, output_type='pdf')
            except Exception as ocr_error:
                return jsonify({"error": f"Error making PDF searchable: {str(ocr_error)}"}), 500
        
        # Convert PDF directly to HTML
        output_html = os.path.join(app.config['OUTPUT_FOLDER'], filename.rsplit('.', 1)[0] + '.html')
        try:
            subprocess.run(['pdf2htmlEX', file_path, output_html], check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Error converting PDF to HTML: {str(e)}"}), 500

    else:
        # For .doc and .docx, convert to HTML using LibreOffice
        output_html = os.path.join(app.config['OUTPUT_FOLDER'], filename.rsplit('.', 1)[0] + '.html')
        try:
            convert_command = [
                'libreoffice',
                '--headless',
                '--convert-to', 'html',
                '--outdir', app.config['OUTPUT_FOLDER'],
                file_path
            ]
            subprocess.run(convert_command, check=True)
        except subprocess.CalledProcessError as e:
            return jsonify({"error": f"Error converting document to HTML: {str(e)}"}), 500

    # Return the HTML URL for display in the viewer
    return jsonify({"html_url": f"/outputs/{filename.rsplit('.', 1)[0]}.html"})

# Serve the converted HTML file
@app.route('/outputs/<filename>')
def serve_output(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')