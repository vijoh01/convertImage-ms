from flask import Flask, request, send_file
from flask_cors import CORS
from PIL import Image
import os
import imageio
from av import open as av_open

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

def convert_heic_to_jpeg(heic_file_path, output_file_path):
    # Use imageio to convert HEIC to JPEG
    im = imageio.imread(heic_file_path)
    imageio.imsave(output_file_path, im)

def decode_avif(avif_file_path):
    # Use pyav to decode AVIF
    container = av_open(avif_file_path)
    for frame in container.decode(video=0):
        frame.to_image().save(avif_file_path, 'AVIF')

@app.route('/api/convert', methods=['POST'])
def handle_image_conversion():
    print('API route hit')

    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400

    file = request.files['file']
    format = request.form.get('format')

    print('Received file:', file.filename)
    print('Received format:', format)

    if not file or not is_valid_format(format) or not is_valid_image_format(file.stream):
        print('Invalid file or image format')
        return {'error': 'Invalid file or image format'}, 400

    input_file_path = f'/opt/render/project/src/uploads/{file.filename}'
    output_file_name = f'converted.{format.lower()}'
    output_file_path = f'/opt/render/project/src/public/{output_file_name}'  # Adjust the path as needed

    try:
        print('Converting image...')

        # Use Pillow for image processing
        image = Image.open(file.stream)

        # Convert to RGB if image mode is RGBA
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        # Save HEIC, HEIF, and AVIF using specific handling
        if format.lower() == 'heic':
            convert_heic_to_jpeg(input_file_path, output_file_path)
        elif format.lower() == 'avif':
            decode_avif(input_file_path)
        else:
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
            if os.path.exists(input_file_path):
                os.remove(input_file_path)
                print('Deleted input file:', input_file_path)
            else:
                print('Input file does not exist:', input_file_path)
        except Exception as delete_error:
            print(f'Error deleting input file: {delete_error}')

if __name__ == '__main__':
    if not os.path.exists('./uploads'):
        os.makedirs('./uploads')

    if not os.path.exists('./public'):
        os.makedirs('./public')

    app.run(debug=True, port=5000)
