from flask import Flask, request, send_file
from flask_cors import CORS
import os
import shutil
import imageio

app = Flask(__name__)
CORS(app)

def is_valid_format(format):
    valid_formats = ['heic', 'heif', 'avif', 'jpeg', 'jpg', 'png', 'tiff', 'webp', 'gif']
    return format.lower() in valid_formats

def is_valid_image_format(file_path):
    try:
        imageio.imread(file_path)
        return True
    except Exception as e:
        print('Error checking image format:', str(e))
        return False

@app.route('/api/convert', methods=['POST'])
def convert_image():
    print('API route hit')

    # Create a temporary directory for storing files
    temp_dir = 'temp'
    os.makedirs(temp_dir, exist_ok=True)

    try:
        # Save the uploaded file to a temporary location
        uploaded_file = request.files['file']
        uploaded_file_path = os.path.join(temp_dir, uploaded_file.filename)
        uploaded_file.save(uploaded_file_path)

        format = request.form.get('format')

        print('Received file:', uploaded_file_path)
        print('Received format:', format)

        if not uploaded_file or not is_valid_format(format) or not is_valid_image_format(uploaded_file_path):
            print('Invalid file or image format')
            return {'error': 'Invalid file or image format'}, 400

        output_file_name = 'converted.' + format
        output_file_path = os.path.join(os.getcwd(), 'public', output_file_name)

        try:
            print('Converting image...')

            # Use imageio to read and write images
            img = imageio.imread(uploaded_file_path)
            imageio.imwrite(output_file_path, img, format=format)

            print('Conversion successful')

            # Set response headers for download
            return send_file(output_file_path, as_attachment=True, download_name=output_file_name)

        except Exception as conversion_error:
            print('Error during conversion:', str(conversion_error))
            return {'error': 'Conversion failed'}, 500

        finally:
            # Delete the temporary directory
            shutil.rmtree(temp_dir, ignore_errors=True)

    except Exception as e:
        print('Error:', str(e))
        return {'error': 'Internal Server Error'}, 500

if __name__ == '__main__':
    app.run(debug=True)