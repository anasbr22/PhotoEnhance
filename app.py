from flask import Flask, render_template, send_from_directory, request, jsonify
from PIL import Image, ImageFilter
import os

app = Flask(__name__)

# Dossier où les images seront stockées temporairement
UPLOAD_FOLDER = 'temp_uploads'
ENHANCED_FOLDER = 'temp_enhanced'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENHANCED_FOLDER'] = ENHANCED_FOLDER

# Fonction pour nettoyer les dossiers au démarrage
def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)  # Créer le dossier s'il n'existe pas
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Supprimer le fichier ou le lien
            elif os.path.isdir(file_path):
                os.rmdir(file_path)  # Supprimer le dossier vide (s'il y en a)
        except Exception as e:
            print(f"Erreur lors de la suppression de {file_path}: {e}")

# Nettoyer les dossiers à chaque démarrage de l'application
clear_folder(UPLOAD_FOLDER)
clear_folder(ENHANCED_FOLDER)

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
    enhance_times = int(request.form.get('enhance_times', 1))  # Récupère le nombre d'améliorations, valeur par défaut = 1

    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Sauvegarder l'image téléchargée
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    # Chemin pour l'image améliorée
    enhanced_image_path = os.path.join(app.config['ENHANCED_FOLDER'], 'enhanced_' + image.filename)

    # Vérifier si une image existe déjà avec le même nom et la supprimer si elle existe
    if os.path.exists(enhanced_image_path):
        os.remove(enhanced_image_path)
        print(f"Ancienne image supprimée : {enhanced_image_path}")

    # Ouvrir et traiter l'image
    with Image.open(image_path) as img:


# Model *****************************************************************************************************************

        # Appliquer l'amélioration plusieurs fois (par exemple, rotation)
        for i in range(enhance_times):
            img = img.rotate(30)  # Exemple de transformation (rotation)
            print(f"amélioration {i + 1}")

# *************************************************************************************************************



        # Sauvegarder l'image améliorée
        img.save(enhanced_image_path)

    # Renvoyer l'URL de l'image traitée
    enhanced_image_url = f"/enhanced/{'enhanced_' + image.filename}"
    return jsonify({'enhanced_image_url': enhanced_image_url})


# Route pour servir l'image traitée
@app.route('/enhanced/<filename>')
def send_enhanced_image(filename):
    print(f"Request for enhanced image: {filename}")
    return send_from_directory(app.config['ENHANCED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
