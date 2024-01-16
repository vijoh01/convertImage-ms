from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import io

app = Flask(__name__)
CORS(app)

@app.route('/convert_image', methods=['POST'])
def convert_image_route():
    print('API route hit')
    
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']
    format = request.form.get('format')
    
    if not format or format.upper() not in ["JPEG", "PNG", "BMP", "TIFF", "WEBP", "GIF", "ICO", "JP2", "AVIF"]:
        return {'error': 'Invalid or unsupported output format'}, 400

    try:
        # Read the image
        image = Image.open(file)

        # Convert the image
        output_image = convert_image_pillow(image, format)

        # Save the converted image to a buffer
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format=format)

        # Return the converted image as a response
        return {'converted_image': output_buffer.getvalue().decode('ISO-8859-1')}
    
    except Exception as e:
        return {'error': f'Error converting image: {str(e)}'}, 500

def convert_image_pillow(image, output_format):
    try:
        # Save using Pillow
        output_image = Image.new("RGB", image.size)
        output_image.paste(image)
        return output_image
    except Exception as e_pillow:
        print(f"Pillow conversion error: {e_pillow}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
