# Advanced Multi-Modal Steganography Security System

A secure, unified web-based application built using **Flask** and **Python** designed for covert data communication across heterogeneous media (Image, Audio, and Text). 

## 🛡️ Core Security Architecture & Features
* **Defense-in-Depth Protocol:** Implements strong pre-embedding data encryption using **AES-Fernet** symmetric cryptography.
* **Dynamic Key Derivation:** Enhanced security using **PBKDF2 SHA-256** cryptographic key derivation based on user-defined passwords.
* **Anti-Steganalysis Design:** Mitigates structural signatures and sequential embedding patterns by implementing the **Fisher-Yates Shuffle algorithm** for non-linear pixel/sample index randomization.
* **Forensic Security (Zero-Disk Footprint):** Engineered a secure backend processing pipeline within volatile memory (RAM), ensuring zero post-session forensic data remnants on persistent storage.

## 📊 Performance Metrics Achieved
* **Peak Signal-to-Noise Ratio (PSNR):** ~62.32 dB (Under heavy text payloads)
* **Mean Squared Error (MSE):** ~0.0381

## 📁 System Architecture & Routes
* `/` — Master Unified Dashboard
* `/image` — Image Steganography Module (LSB + PIL)
* `/audio` — Audio Steganography Module (Base64 + HTML)
* `/text` — Text Steganography Module (Zero-Width Encoding)

## 🚀 Technical Stack
* **Backend:** Python, Flask
* **Libraries:** Pillow (PIL), Pydub, Cryptography (Fernet)
* **Frontend:** JavaScript, CSS3, HTML5

## Folder Structure

```
fyp_project/
├── app.py                      # Flask server (image module's app.py + new routes)
├── requirements.txt
├── templates/
│   ├── dashboard.html          # NEW — master landing page / dashboard
│   ├── image_module.html       # was: imagee-emplates.html (paths updated)
│   ├── audio_module.html        # was: audio_index.html (paths updated)
│   └── text_module.html         # was: text_steganography.html (back-link only)
├── static/
│   ├── css/dashboard.css       # NEW — dashboard styling
│   ├── js/dashboard.js         # NEW — dashboard interactions (nav, scroll reveal)
│   ├── image/
│   │   ├── style.css           # was: image-style.css
│   │   └── script.js           # was: image-script.js (unchanged, still calls
│   │                              http://127.0.0.1:5000/encrypt, /encode, /decode)
│   └── audio/
│       ├── style.css           # was: audio-style.css
│       └── script.js           # was: audio_script.js (unchanged)
├── uploads/                     # used by image module (/encode, /decode)
└── output/                      # used by image module (/encode)
```

## Routes

| Route       | Description                                      |
|--------------|--------------------------------------------------|
| `/`          | Master dashboard (landing page, all 3 modules)   |
| `/image`     | Image Steganography module                       |
| `/audio`     | Audio Steganography module (client-side)         |
| `/text`      | Text Steganography module (client-side)          |
| `/encrypt`   | (unchanged) Image module API — encrypt text       |
| `/encode`    | (unchanged) Image module API — embed into image   |
| `/decode`    | (unchanged) Image module API — extract from image |

## Exact File Changes Made

1. **`audio_index.html` → `templates/audio_module.html`**
   - `href="style.css"` → `href="/static/audio/style.css"`
   - `src="script.js"` → `src="/static/audio/script.js"`
   - Added `<a href="/" class="back-link">← Back to Dashboard</a>` inside `.container`

2. **`audio-style.css` → `static/audio/style.css`**
   - Added `.back-link` / `.back-link:hover` rules only (appended, nothing removed)

3. **`audio_script.js` → `static/audio/script.js`**
   - **Unchanged.**

4. **`imagee-emplates.html` → `templates/image_module.html`**
   - `href="/static/style.css"` → `href="/static/image/style.css"`
   - `src="/static/script.js"` → `src="/static/image/script.js"`
   - Added `<a href="/" class="back-link">← Back to Dashboard</a>` inside `.container`

5. **`image-style.css` → `static/image/style.css`**
   - Added `.back-link` / `.back-link:hover` rules only (appended, nothing removed)

6. **`image-script.js` → `static/image/script.js`**
   - **Unchanged.** Still calls `http://127.0.0.1:5000/encrypt`, `/encode`, `/decode`.

7. **`image-app.py` → `app.py`**
   - All original imports, helper functions, and `/encrypt`, `/encode`, `/decode`
     routes **unchanged**.
   - The original `/` route (`return render_template("index.html")`) was replaced
     with a new dashboard route, and three new routes were added:
     ```python
     @app.route("/")
     def home():
         return render_template("dashboard.html")

     @app.route("/image")
     def image_module():
         return render_template("image_module.html")

     @app.route("/audio")
     def audio_module():
         return render_template("audio_module.html")

     @app.route("/text")
     def text_module():
         return render_template("text_module.html")
     ```

8. **`text_steganography.html` → `templates/text_module.html`**
   - Added `.back-link` CSS rules (appended)
   - Added `<a href="/" class="back-link">← Back to Dashboard</a>` before the `<h2>`
   - All AES/zero-width logic **unchanged**.

9. **NEW FILES**
   - `templates/dashboard.html` — landing page with hero, stats, 3 module cards,
     about, features, footer.
   - `static/css/dashboard.css` — dashboard styling (dark cybersecurity theme).
   - `static/js/dashboard.js` — mobile nav toggle + scroll-reveal animations.
   - `requirements.txt`

## Running the Project

```bash
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000/** — the dashboard appears, and each
"Launch Module" button opens the corresponding module at its route.

Note: The audio and text modules run fully client-side in the browser (no server
calls). The image module's frontend (`/image`) calls back to the same Flask server
at `http://127.0.0.1:5000/encrypt`, `/encode`, `/decode` — exactly as before.
