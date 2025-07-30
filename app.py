from flask import Flask, request, jsonify, send_file, render_template
from sbi_analysis import analyze_sbi_statement
import os

app = Flask(__name__, static_folder='static', template_folder='templates')

#to display images on webpage
from flask import send_from_directory

@app.route('/reports/<path:filename>')
def serve_report_file(filename):
    return send_from_directory('reports', filename)


# Serve the HTML page
@app.route('/')
def home():
    return render_template('index.html')

# Handle file upload and processing
@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:  # ✅ match the HTML input name
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']     # ✅ match the HTML input name
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'Only .csv files supported'}), 400

    os.makedirs('uploads', exist_ok=True)
    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    result = analyze_sbi_statement(file_path)

    return jsonify(result)

# Allow downloading files if needed
@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
