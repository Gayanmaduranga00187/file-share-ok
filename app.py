from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Uploads Folder එක සැකසීම
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template එකට Logo එක එකතු කර ඇත
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Share App</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            color: #333;
            padding: 20px;
            text-align: center;
            min-height: 100vh;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 15px;
            max-width: 600px;
            margin: auto;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        /* Logo එක සඳහා CSS */
        .logo {
            width: 100px; /* Logo එකේ ප්‍රමාණය මෙතනින් වෙනස් කරන්න */
            height: auto;
            margin-bottom: 10px;
        }
        header {
            margin-bottom: 25px;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }
        .creator { font-size: 13px; color: #888; margin-top: 5px; }
        h2 { color: #2c3e50; margin: 5px 0; }
        
        form { margin: 20px 0; }
        ul { list-style: none; padding: 0; }
        li { 
            background: #f9f9f9; 
            margin: 10px 0; 
            padding: 12px; 
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border: 1px solid #eee;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            font-weight: 500;
        }
        .upload-btn { background: #3498db; color: white; }
        .download-btn { background: #2ecc71; color: white; }
        .delete-btn { background: #e74c3c; color: white; margin-left: 5px; }

        #progress {
            width: 100%;
            background-color: #f1f1f1;
            border-radius: 10px;
            margin: 20px 0;
            display: none;
            overflow: hidden;
        }
        #progress-bar {
            height: 15px;
            width: 0;
            background-color: #3498db;
            text-align: center;
            color: white;
            line-height: 15px;
            font-size: 10px;
            transition: width 0.3s;
        }
    </style>
    <script>
        function uploadFiles(event) {
            event.preventDefault();
            let form = document.getElementById('upload-form');
            let formData = new FormData(form);
            let xhr = new XMLHttpRequest();

            document.getElementById('progress').style.display = 'block';

            xhr.open('POST', '/');
            xhr.upload.addEventListener('progress', function(event) {
                if (event.lengthComputable) {
                    let percentComplete = (event.loaded / event.total) * 100;
                    let progressBar = document.getElementById('progress-bar');
                    progressBar.style.width = percentComplete + '%';
                    progressBar.textContent = Math.round(percentComplete) + '%';
                }
            });

            xhr.onload = function() {
                if (xhr.status === 200) { location.reload(); }
                else { alert('Error uploading file!'); }
            };
            xhr.send(formData);
        }
    </script>
</head>
<body>
    <div class="container">
        <header>
            <img src="/logo.png" alt="App Logo" class="logo">
            <h2>File Share App</h2>
            <div class="creator">Created by Gayan Maduranga</div>
        </header>

        <form id="upload-form" enctype="multipart/form-data" onsubmit="uploadFiles(event)">
            <input type="file" name="file" multiple required>
            <button type="submit" class="upload-btn btn">Upload</button>
        </form>

        <div id="progress"><div id="progress-bar">0%</div></div>

        <h3 style="text-align: left; color: #555;">Uploaded Files</h3>
        <ul>
            {% for file in files %}
            <li>
                <span style="font-size: 14px; color: #444; word-break: break-all; padding-right: 10px;">{{ file }}</span>
                <div style="display: flex;">
                    <a href="/download/{{ file }}" class="btn download-btn">Download</a>
                    <form method="POST" action="/delete/{{ file }}" style="display:inline; margin: 0;">
                        <button type="submit" class="btn delete-btn">Delete</button>
                    </form>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "OK", 200

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HTML_TEMPLATE, files=files)

# Logo එක පෙන්වීමට අවශ්‍ය Route එක
@app.route("/logo.png")
def get_logo():
    # ඔයාගේ python file එක තියෙන තැනම 'logo.png' නමින් image එකක් තිබිය යුතුයි
    return send_from_directory(".", "logo.png")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("upload_file"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)