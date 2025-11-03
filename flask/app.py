from flask import Flask, request, render_template_string, redirect, url_for, send_from_directory
import shutil
import os
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4'}

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Servidor Familia Díaz</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='servidor_casa.css') }}">
</head>
<body>
    <nav class='side-bar-nav'>
        <a href="{{ url_for('upload_file', path='') }}" class='title'>
            <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='white' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-folder'><path d='M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z'/></svg>
            <h1>Inicio</h1>
        </a>
        <div class='options-container'>
            <a class='option-side-bar'>
                <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-home'><path d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/><polyline points='9 22 9 12 15 12 15 22'/></svg>
                <p>Inicio</p>
            </a>
            <a href="{{ url_for('upload_file', path='documentos') }}" class='option-side-bar'>
                <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-file-text'><path d='M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z'/><polyline points='14 2 14 8 20 8'/><line x1='16' y1='13' x2='8' y2='13'/><line x1='16' y1='17' x2='8' y2='17'/><polyline points='10 9 9 9 8 9'/></svg>
                <p>Documentos</p>
            </a>
            <a href="{{ url_for('upload_file', path='imagenes') }}" class='option-side-bar'>
                <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-image'><rect x='3' y='3' width='18' height='18' rx='2' ry='2'/><circle cx='8.5' cy='8.5' r='1.5'/><polyline points='21 15 16 10 5 21'/></svg>
                <p>Imágenes</p>
            </a>
            <a href="{{ url_for('upload_file', path='videos') }}" class='option-side-bar'>
                <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-video'><polygon points='23 7 16 12 23 17 23 7'/><rect x='1' y='5' width='15' height='14' rx='2' ry='2'/></svg>
                <p>Videos</p>
            </a>
        </div>
        <div class='storage-box'>
            <div class='storage-title-svg'>
                <svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='feather feather-cloud'><path d='M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z'/></svg>
                <p>Almacenamiento</p>
            </div>
            <div class='storage-bar-box'>
                <div class='storage-bar' style="width: {{ (used_gb / total_gb)*100 }}%;"> </div>
            </div>
            <span class='storage-availability-display-message'>
                {{ '%.2f' % used_gb }} GB usados de {{ '%.2f' % total_gb }} GB ({{ '%.1f' % ((used_gb / total_gb)*100) }}%)
            </span>
        </div>
    </nav>
    <div class="main-section">
        <div class="input_section">
            <form class="file_box" id="uploadForm" enctype="multipart/form-data">
                <label for="file-upload" class="upload_file transparent_blue_bg"> + </label>
                <input id="file-upload" type="file" name="file" multiple>
                <p class="input_box_title">Sube un archivo</p>
                <p class="input_box_description">Arrastra o selecciona archivos que deseas guardar en el servidor</p>
            </form>
            <form class="file_box" method="post" action="{{ url_for('create_folder', path=path) }}">
                <button class="upload_file transparent_yellow_bg" type="submit"> + </button>
                <p class="input_box_title">Crea una carpeta</p>
                <input type="text" name="foldername" placeholder="Nombre" required>
                <p class="input_box_description">Secciona los archivos a tu gusto, creando compartimientos con nombres personalizados</p>
            </form>
        </div>
        <div id="globalProgressContainer">
            <div id="globalProgressBar"></div>
        </div>
        <ul id="uploadStatus"></ul>
        <script>
        document.getElementById('file-upload').addEventListener('change', async function () {
        const files = this.files;
        const totalFiles = files.length;
        const path = window.location.pathname;

        const globalBar = document.getElementById('globalProgressBar');
        const uploadStatus = document.getElementById('uploadStatus');

        uploadStatus.textContent = '';
        globalBar.style.width = '0%';

        let uploadedCount = 0;

        for (let i = 0; i < totalFiles; i++) {
            const file = files[i];
            const formData = new FormData();
            formData.append('file', file);

            try {
            await new Promise((resolve, reject) => {
                const xhr = new XMLHttpRequest();
                xhr.open('POST', path, true);

                xhr.onload = function () {
                if (xhr.status === 200 || xhr.status === 302) {
                    uploadedCount++;
                    const percent = (uploadedCount / totalFiles) * 100;
                    globalBar.style.width = `${percent.toFixed(1)}%`;
                    uploadStatus.innerText = `Subido ${uploadedCount} de ${totalFiles} archivos`;
                    resolve();
                } else {
                    uploadStatus.innerText += `\n❌ Error al subir ${file.name}`;
                    reject();
                }
                };

                xhr.onerror = function () {
                uploadStatus.innerText += `\n❌ Error al subir ${file.name}`;
                reject();
                };

                xhr.send(formData);
            });
            } catch (err) {
            // El error ya se mostró
            }
        }

        // Al terminar
        if (uploadedCount === totalFiles) {
            uploadStatus.innerText += `\n✅ Todos los archivos fueron subidos correctamente`;
            setTimeout(() => location.reload(), 1500);
        }
        });
        </script>
        <div class="media_section">
            <div class="media_inside">
                <p> Archivos - </p>
                <div class="media_div">
                {% for folder in folders %}
                    <div class="media_item" style="position: relative;">
                        
                        <form action="{{ url_for('delete_file', file_path=(path + '/' + folder) if path else folder) }}"
                            method="post"
                            style="position: absolute; top: 5px; right: 5px;">
                            <button type="submit"
                                    onclick="return confirm('¿Estás seguro de que deseas eliminar esta carpeta?')"
                                    style="background: transparent; border: none; cursor: pointer;">
                                🗑️
                            </button>
                        </form>
                        
                        <a href="{{ url_for('upload_file', path=path ~ '/' ~ folder if path else folder) }}">
                            <img src="{{ url_for('static', filename='folder_icon.png') }}" style="width: 150px; height: 150px; object-fit: cover;"">
                        </a>
                        <p class="media_item_title"> {{folder}} </p>
                    </div>
                {% endfor %}
                {% for file in files %}
                    <div class="media_item" style="position: relative;">
                        {% if file.endswith(('.png', '.jpg', '.jpeg', '.gif')) %}
                            
                            <form action="{{ url_for('delete_file', file_path=path + '/' + file if path else file) }}" method="post" style="position: absolute; top: 5px; right: 5px;">
                                <button type="submit" onclick="return confirm('¿Estás seguro de que deseas eliminar esta imagen?')" style="background: transparent; border: none; cursor: pointer;">
                                    🗑️
                                </button>
                            </form>
                            <a href="{{ url_for('uploaded_file', filename=(path ~ '/' if path else '') ~ file) }}">
                                <img src="{{ url_for('uploaded_file', filename=(path ~ '/' if path else '') ~ file) }}"
                                    style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px;">
                            </a>
                            <p class="media_item_title">{{ file }}</p>

                        {% elif file.endswith('.mp4') %}
                            <div class="thumbnail-container" style="position: relative;">
                                
                                <form action="{{ url_for('delete_file', file_path=path + '/' + file if path else file) }}" method="post"
                                    style="position: absolute; top: 5px; right: 5px;">
                                    <button type="submit"
                                            onclick="return confirm('¿Estás seguro de que deseas eliminar esta imagen?')"
                                            style="background: transparent; border: none; cursor: pointer;">
                                        🗑️
                                    </button>
                                </form>
                                
                                <a href="{{ url_for('uploaded_file', filename=(path ~ '/' if path else '') ~ file) }}">
                                    <img src="{{ url_for('uploaded_file', filename=(path ~ '/' if path else '') ~ file.rsplit('.', 1)[0] ~ '.jpg') }}"
                                        style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px;"
                                        alt="video thumbnail" class="thumbnail-img">
                                    <div class="play-icon" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                        font-size: 36px; color: white; text-shadow: 0px 0px 5px black;">&#9658;</div>
                                </a>
                            </div>
                            <p class="media_item_title">{{ file }}</p>
                        {% endif %}
                    </div>
                {% endfor %}
                </div>
            </div>
            <div style="margin: 20px; width: 90%; max-width: 600px;">
                <p>Espacio en disco del servidor:</p>
                <div style="background: #ddd; border-radius: 10px; width: 100%; height: 20px; position: relative;">
                    <div style="background: #4caf50; height: 100%; border-radius: 10px; width: {{ (used_gb / total_gb)*100 }}%;"></div>
                    <span style="position: absolute; width: 100%; text-align: center; top: 0; left: 0; font-weight: bold; font-size: 12px;">
                        {{ '%.2f' % used_gb }} GB usados de {{ '%.2f' % total_gb }} GB ({{ '%.1f' % ((used_gb / total_gb)*100) }}%)
                    </span>
                </div>
                <p>Libre: {{ '%.2f' % free_gb }} GB</p>
            </div>
        </div>
    </div>
    
</body>
</html>
'''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def safe_join(base, *paths):
    final_path = os.path.normpath(os.path.join(base, *paths))
    if not os.path.abspath(final_path).startswith(os.path.abspath(base)):
        raise ValueError("Ruta no permitida")
    return final_path

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/create-folder', defaults={'path': ''}, methods=['POST'])
@app.route('/<path:path>/create-folder', methods=['POST'])
def create_folder(path):
    foldername = request.form.get('foldername')
    current_path = safe_join(app.config['UPLOAD_FOLDER'], path)
    if foldername:
        folder_path = os.path.join(current_path, foldername)
        os.makedirs(folder_path, exist_ok=True)
    return redirect(url_for('upload_file', path=path))

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def upload_file(path):
    current_path = safe_join(app.config['UPLOAD_FOLDER'], path)
    os.makedirs(current_path, exist_ok=True)

    if request.method == 'POST':
        files = request.files.getlist('file')
        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(current_path, filename)
                file.save(filepath)

                # Si es video, generar miniatura
                if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                    thumbnail_path = os.path.join(current_path, filename.rsplit('.', 1)[0] + '.jpg')
                    try:
                        subprocess.run([
                            'ffmpeg',
                            '-i', filepath,
                            '-ss', '00:00:01.000',
                            '-vframes', '1',
                            thumbnail_path
                        ], check=True)
                    except subprocess.CalledProcessError as e:
                        print(f'Error generando miniatura: {e}')
        return redirect(request.url)

    items = os.listdir(current_path)
    files = [f for f in items if os.path.isfile(os.path.join(current_path, f))]
    folders = [f for f in items if os.path.isdir(os.path.join(current_path, f))]

    rel_path = path.strip('/')

    # Obtener info de disco raíz
    total, used, free = shutil.disk_usage('/')

    # Pasar a MB o GB para mostrar más legible
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)

    return render_template_string(
        HTML,
        files=files,
        folders=folders,
        path=rel_path,
        total_gb=total_gb,
        used_gb=used_gb,
        free_gb=free_gb
    )

def generate_thumbnail(video_path, thumbnail_path):
    try:
        subprocess.run([
            "ffmpeg",
            "-i", video_path,
            "-ss", "00:00:01.000",  # 1 segundo (ajustable)
            "-vframes", "1",
            "-q:v", "2",  # calidad
            thumbnail_path
        ], check=True)
    except subprocess.CalledProcessError:
        print("Error al generar la miniatura")

@app.route('/delete-file/<path:file_path>', methods=['POST'])
def delete_file(file_path):
    full_path = safe_join(app.config['UPLOAD_FOLDER'], file_path)
    if os.path.exists(full_path):
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                shutil.rmtree(full_path)
        except Exception:
            pass
    return redirect(request.referrer or url_for('upload_file'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
