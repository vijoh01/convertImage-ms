from flask import Flask, request, send_file
from flask_cors import CORS
import os
from PIL import Image
import pyheif
import avif

app = Flask(__name__)
CORS(app)

def is_valid_format(format):
    valid_formats = ['heic', 'heif', 'avif', 'jpeg', 'jpg', 'png', 'tiff', 'webp', 'gif']
    return format.lower() in valid_formats

def is_valid_image_format(file_path):
    try:
        Image.open(file_path).verify()
        return True
    except Exception as e:
        print(f'Error checking image format: {e}')
        return False

@app.route('/api/convert', methods=['POST'])
def handle_image_conversion():
    print('API route hit')

    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']
    format = request.form.get('format')

    print('Received file:', file.filename)
    print('Received format:', format)

    if not file or not is_valid_format(format):
        print('Invalid file or format')
        return {'error': 'Invalid file or format'}, 400

    input_file_path = f'/opt/render/project/src/uploads/{file.filename}'
    output_file_name = f'converted.{format.lower()}'
    output_file_path = f'/opt/render/project/src/public/{output_file_name}'  # Adjust the path as needed

    try:
        # Save the file before processing
        file.save(input_file_path)

        print('Converting image...')

        if format.lower() in ['heic', 'heif']:
            # Use pyheif to convert HEIC and HEIF to JPEG
            heif_file = pyheif.read(input_file_path)
            image = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )
            image.save(output_file_path, format="JPEG")
        elif format.lower() == 'avif':
            # Use avif to convert AVIF to JPEG
            avif_data = avif.read(input_file_path)
            image = Image.frombytes('RGB', (1, 1), avif_data)
            image.save(output_file_path, format="JPEG")
        else:
            # Use Pillow for other formats
            image = Image.open(input_file_path)

            # Convert to RGB if image mode is RGBA
            if image.mode == 'RGBA':
                image = image.convert('RGB')

            image.save(output_file_path, format=format.upper())

        print('Conversion successful')

        # Set response headers for download
        return send_file(output_file_path, as_attachment=True, download_name=output_file_name)
    except Exception as e:
        print(f'Error during conversion: {e}')
        return {'error': 'Conversion failed'}, 500
    finally:
        try:
            # Delete the input file
            os.remove(input_file_path)
            print('Deleted input file:', input_file_path)
        except Exception as delete_error:
            print(f'Error deleting input file: {delete_error}')

if __name__ == '__main__':
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')

    if not os.path.exists('./public'):
        os.makedirs('./public')

    app.run(debug=True, port=5000)
