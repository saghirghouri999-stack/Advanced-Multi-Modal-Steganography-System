from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from PIL import Image
from cryptography.fernet import Fernet
# Password based key derivation functions for dynamic cryptographic keys
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
from werkzeug.utils import secure_filename
import os
import random

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    # Master dashboard for the Multi-Modal Steganography Security System
    return render_template("dashboard.html")

@app.route("/image")
def image_module():
    # Launches the Image Steganography module (unchanged logic)
    return render_template("image_module.html")

@app.route("/audio")
def audio_module():
    # Launches the Audio Steganography module (unchanged logic)
    return render_template("audio_module.html")

@app.route("/text")
def text_module():
    # Launches the Text Steganography module (unchanged logic)
    return render_template("text_module.html")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Fixed Salt for Key Derivation (Must be same for encryption & decryption)
SALT = b'FYP_Stego_Secure_Salt_123'

# Function to derive a unique Fernet Key from the user's password
def generate_key_from_password(password: str) -> Fernet:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000
    )
    derived_key = kdf.derive(password.encode())
    fernet_key = base64.urlsafe_b64encode(derived_key)
    return Fernet(fernet_key)

def text_to_bits(data):
    return ''.join(format(byte, '08b') for byte in data)

def bits_to_bytes(bits):
    return bytes(
        int(bits[i:i + 8], 2)
        for i in range(0, len(bits), 8)
    )

def generate_random_positions(width, height, total_bits, seed=12345):
    positions = [
        (x, y)
        for y in range(height)
        for x in range(width)
    ]
    random.seed(seed)
    random.shuffle(positions)
    return positions[:total_bits]

def embed_bits_lsb(img, bitstream, seed=12345):
    pixels = img.load()
    width, height = img.size
    total_capacity = width * height

    if len(bitstream) > total_capacity:
        raise ValueError("Message too large for selected image.")

    positions = generate_random_positions(width, height, len(bitstream), seed)

    for index, (x, y) in enumerate(positions):
        r, g, b = pixels[x, y]
        r = (r & ~1) | int(bitstream[index])
        pixels[x, y] = (r, g, b)

    return img

def extract_bits(img, total_bits, seed=12345):
    pixels = img.load()
    width, height = img.size
    positions = generate_random_positions(width, height, total_bits, seed)
    extracted_bits = []

    for (x, y) in positions:
        r, g, b = pixels[x, y]
        extracted_bits.append(str(r & 1))

    return ''.join(extracted_bits)

@app.route("/encrypt", methods=["POST"])
def encrypt_text():
    try:
        data = request.json
        secret_text = data.get("text")
        password = data.get("password")

        if not password:
            return jsonify({"error": "Password is required for encryption"}), 400

        # Generate unique key dynamically from user password
        cipher = generate_key_from_password(password)
        encrypted = cipher.encrypt(secret_text.encode())
        
        return jsonify({
            "encrypted_text": encrypted.decode(),
            "message": "Text encrypted successfully"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/encode", methods=["POST"])
def encode_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image_file = request.files['image']
        encrypted_text = request.form.get("encrypted_text")

        if not encrypted_text:
            return jsonify({"error": "Encrypted text missing. Please encrypt first."}), 400

        filename = secure_filename(image_file.filename)
        if not filename:
            filename = f"upload_{random.randint(1000, 9999)}.jpg"

        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        img = Image.open(image_path).convert("RGB")

        encrypted_bytes = encrypted_text.encode()
        payload_length = len(encrypted_bytes)
        header = payload_length.to_bytes(4, byteorder='big')
        final_payload = header + encrypted_bytes

        bitstream = text_to_bits(final_payload)
        stego_img = embed_bits_lsb(img, bitstream)

        base_name = os.path.splitext(filename)[0]
        output_filename = f"{base_name}_stego.png"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        stego_img.save(output_path, "PNG")

        return send_file(os.path.abspath(output_path), as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/decode", methods=["POST"])
def decode_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400

        image_file = request.files['image']
        password = request.form.get("password") # Get password from frontend

        if not password:
            return jsonify({"error": "Password required to decrypt data"}), 400

        filename = secure_filename(image_file.filename)
        if not filename:
            filename = f"decode_{random.randint(1000, 9999)}.png"

        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image_file.save(image_path)

        img = Image.open(image_path).convert("RGB")

        header_bits = extract_bits(img, 32)
        header_bytes = bits_to_bytes(header_bits)
        payload_length = int.from_bytes(header_bytes, byteorder='big')

        if payload_length <= 0 or payload_length > 100000:
            return jsonify({"error": "No hidden data found or image structure is invalid."}), 400

        total_bits = 32 + (payload_length * 8)
        full_bits = extract_bits(img, total_bits)
        payload_bits = full_bits[32:]

        encrypted_bytes = bits_to_bytes(payload_bits)
        
        # Generate the dynamic key for decryption using provided password
        try:
            cipher = generate_key_from_password(password)
            decrypted_message = cipher.decrypt(encrypted_bytes).decode()
        except Exception:
            # If decryption fails, it strictly means the password was wrong
            return jsonify({"error": "Incorrect password! Access Denied."}), 403

        return jsonify({
            "hidden_message": decrypted_message
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)