from flask import Flask, request, render_template_string, send_from_directory, redirect, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Uploads ලබාගන්නා Folder එක සැකසීම
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML Template එක
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Share App</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #74ebd5 0%, #9face6 100%);
            color: #333;
            padding: 20px;
            text-align: center;
            min-height: 100vh;
        }
        .container {
            background: rgba(255, 255, 255, 0.9);
            padding: 30px;
            border-radius: 15px;
            max-width: 600px;
            margin: auto;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        header {
            border-bottom: 2px solid #eee;
            margin-bottom: 20px;
            padding-bottom: 10px;
        }
        .creator { font-size: 12px; color: #777; margin-top: 5px; }
        h2 { color: #2c3e50; }
        form { margin: 20px 0; }
        ul { list-style: none; padding: 0; text-align: left; }
        li { 
            background: #fff; 
            margin: 10px 0; 
            padding: 10px; 
            border-radius: 8px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        button, .btn {
            padding: 8px 15px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            text-decoration: none;
            font-size: 14px;
            transition: 0.3s;
        }
        .upload-btn { background: #3498db; color: white; }
        .delete-btn { background: #e74c3c; color: white; margin-left: 5px; }
        .download-btn { background: #2ecc71; color: white; }
        
        #progress {
            width: 100%;
            background-color: #f3f3f3;
            border-radius: 5px;
            margin: 20px 0;
            display: none;
        }
        #progress-bar {
            height: 20px;
            width: 0;
            background-color: #2ecc71;
            text-align: center;
            color: white;
            border-radius: 5px;
            line-height: 20px;
            font-size: 12px;
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
                if (xhr.status === 200) {
                    location.reload();
                } else {
                    alert('Error uploading file!');
                }
            };
            xhr.send(formData);
        }
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h2>File Share App</h2>
            <div class="creator">Created by Gayan Maduranga</div>
        </header>

        <form id="upload-form" enctype="multipart/form-data" onsubmit="uploadFiles(event)">
            <input type="file" name="file" multiple required>
            <button type="submit" class="upload-btn">Upload</button>
        </form>

        <div id="progress">
            <div id="progress-bar">0%</div>
        </div>

        <h3>Uploaded Files</h3>
        <ul>
            {% for file in files %}
            <li>
                <span style="word-break: break-all;">{{ file }}</span>
                <div>
                    <a href="/download/{{ file }}" class="btn download-btn">Download</a>
                    <form method="POST" action="/delete/{{ file }}" style="display:inline;">
                        <button type="submit" class="delete-btn">Delete</button>
                    </form>
                </div>
            </li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

# Home Route
@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_files = request.files.getlist("file")
        for file in uploaded_files:
            if file and file.filename != '':
                filename = secure_filename(file.filename) # ආරක්ෂාව සඳහා filename එක සකසයි
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return "OK", 200 # JS එකට සාර්ථක බව දැනුම් දෙයි

    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template_string(HTML_TEMPLATE, files=files)

# Download Route
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Delete Route
@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for("upload_file"))

if __name__ == "__main__":
    # Render හෝ වෙනත් Hosting එකකදී දෙන Port එක ලබා ගැනීම
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)