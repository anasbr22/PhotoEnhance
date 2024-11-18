from flask import Flask, render_template, send_from_directory, request, jsonify
from PIL import Image
import os

app = Flask(__name__)

# Dossier où les images seront stockées temporairement
UPLOAD_FOLDER = 'temp_uploads'
ENHANCED_FOLDER = 'temp_enhanced'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENHANCED_FOLDER'] = ENHANCED_FOLDER

# Serve assets and vendor folders from the templates directory
@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory(os.path.join(app.root_path, 'templates/assets'), filename)

@app.route('/vendor/<path:filename>')
def serve_vendor(filename):
    return send_from_directory(os.path.join(app.root_path, 'templates/vendor'), filename)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start():
    return render_template('start.html')







# Route pour le traitement de l'image
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Sauvegarder l'image téléchargée
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    # Traiter l'image avec votre modèle (exemple simple ici)
    enhanced_image_path = os.path.join(app.config['ENHANCED_FOLDER'], 'enhanced_' + image.filename)

    # Utilisation de PIL pour exemple, remplacez par votre modèle de traitement
    img = Image.open(image_path)

#Start model******************************************************************************************************************

    img = img.convert("RGB")  # Simule un traitement
   

#END model********************************************************************************************************************

    img.save(enhanced_image_path)

    # Renvoyer l'URL de l'image traitée
    enhanced_image_url = f"/enhanced/{'enhanced_' + image.filename}"
    return jsonify({'enhanced_image_url': enhanced_image_url})






# Route pour servir l'image traitée
@app.route('/enhanced/<filename>')
def send_enhanced_image(filename):
    return send_from_directory(app.config['ENHANCED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
