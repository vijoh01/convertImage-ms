from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import cv2
import io

app = Flask(__name__)
CORS(app)

@app.route('/api/convert', methods=['POST'])
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
        output_image = convert_image(image, format)

        # Save the converted image to a buffer
        output_buffer = io.BytesIO()
        output_image.save(output_buffer, format=format)

        # Return the converted image as a response
        return {'converted_image': output_buffer.getvalue().decode('ISO-8859-1')}
    
    except Exception as e:
        return {'error': f'Error converting image: {str(e)}'}, 500

def convert_image(image, output_format):
    try:
        # Convert the image using Pillow or OpenCV based on the format
        if output_format.upper() in ["JPEG", "PNG", "BMP", "TIFF", "WEBP", "GIF", "ICO", "JP2", "AVIF"]:
            # Use Pillow for supported formats
            output_image = Image.new("RGB", image.size)
            output_image.paste(image)
        else:
            # Use OpenCV for other formats
            output_image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)

        return output_image

    except Exception as e:
        print(f"Error during image conversion: {e}")
        raise

if __name__ == '__main__':
    app.run(debug=True)
