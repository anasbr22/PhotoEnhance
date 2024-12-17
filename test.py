from flask import Flask, render_template, send_from_directory, request, jsonify
from PIL import Image
import os
import torch
import numpy as np
import RRDBNet_arch as arch

# Load the model
model_path = 'models/ESRGAN_x4.pth'
device = torch.device('cpu')
model = arch.RRDBNet(3, 3, 64, 23, gc=32)
model.load_state_dict(torch.load(model_path, map_location=device), strict=True)
model.eval()
model = model.to(device)

app = Flask(__name__)

# Temporary folders for uploads and enhanced images
UPLOAD_FOLDER = 'temp_uploads'
ENHANCED_FOLDER = 'temp_enhanced'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ENHANCED_FOLDER'] = ENHANCED_FOLDER

# Function to clean up folders at startup
def clear_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
        except Exception as e:
            print(f"Error removing {file_path}: {e}")

# Clear folders on startup
clear_folder(UPLOAD_FOLDER)
clear_folder(ENHANCED_FOLDER)

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

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400

    image = request.files['image']
    enhance_times = int(request.form.get('enhance_times', 1))

    if image.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the uploaded image
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    # Path for the enhanced image
    enhanced_image_path = os.path.join(app.config['ENHANCED_FOLDER'], f'enhanced_{image.filename}')

    if os.path.exists(enhanced_image_path):
        os.remove(enhanced_image_path)

    # Process the image
    with Image.open(image_path) as img:
        img = img.convert('RGB')
        img_tensor = torch.from_numpy(np.array(img).transpose(2, 0, 1)).float().unsqueeze(0) / 255.0
        img_tensor = img_tensor.to(device)

        for i in range(enhance_times):
            with torch.no_grad():
                output = model(img_tensor).squeeze(0).cpu().clamp_(0, 1)
                img_tensor = output.unsqueeze(0).to(device)

        # Convert the tensor back to an image
        output_image = (output.permute(1, 2, 0).numpy() * 255).astype(np.uint8)
        enhanced_image = Image.fromarray(output_image)
        enhanced_image.save(enhanced_image_path)

    enhanced_image_url = f"/enhanced/enhanced_{image.filename}"
    return jsonify({'enhanced_image_url': enhanced_image_url})

@app.route('/enhanced/<filename>')
def send_enhanced_image(filename):
    print(f"Request for enhanced image: {filename}")
    return send_from_directory(app.config['ENHANCED_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
