from flask import Flask, request, send_file
from wand.image import Image
import os

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ALLOWED_FORMATS = ['heic', 'heif', 'avif', 'jpeg', 'jpg', 'png', 'tiff', 'webp', 'gif']

@app.route('/api/convert', methods=['POST'])
def convert_image():
    print('API route hit')

    form = request.form
    file = request.files.get('file')
    format = form.get('format')

    print('Received file:', file.filename)
    print('Received format:', format)

    if not file or not is_valid_format(format) or not is_valid_image_format(file):
        print('Invalid file or image format')
        return {'error': 'Invalid file or image format'}, 400

    input_file = file.stream
    output_file_name = 'converted.' + format
    output_file_path = os.path.join('public', output_file_name)  # Adjust the path as needed

    try:
        print('Converting image...')

        with Image(file=input_file) as img:
            img.format = format.upper()
            img.save(filename=output_file_path)

        print('Conversion successful')

        # Set response headers for download
        response = send_file(output_file_path, as_attachment=True, download_name=output_file_name)
        response.headers['Content-Type'] = f'image/{format}'
        return response
    except Exception as e:
        print('Error during conversion:', str(e))
        return {'error': 'Conversion failed'}, 500
    finally:
        try:
            # Delete the output file
            os.remove(output_file_path)
            print('Deleted output file:', output_file_path)
        except Exception as delete_error:
            print('Error deleting output file:', str(delete_error))

def is_valid_format(format):
    return isinstance(format, str) and format.lower() in ALLOWED_FORMATS

def is_valid_image_format(file):
    # Check if the file format is one of the valid image formats
    try:
        Image(file=file.stream).format
        return True
    except Exception as error:
        print('Error checking image format:', str(error))
        return False

if __name__ == '__main__':
    app.run(debug=True)
