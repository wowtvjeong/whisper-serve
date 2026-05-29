from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp, os, tempfile, requests

app = Flask(__name__)
CORS(app)
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.json
    url  = data.get("url", "")
    if not url:
        return jsonify({"error": "URL이 필요합니다"}), 400

    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "audio")
        opts = {
            "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio",
            "outtmpl": out + ".%(ext)s",
            "postprocessors": [],
            "quiet": True,
            "no_warnings": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            ext = info.get("ext", "webm")

        audio_file = out + "." + ext

        with open(audio_file, "rb") as f:
            resp = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {GROQ_KEY}"},
                files={"file": (f"audio.{ext}", f, "audio/webm")},
                data={"model": "whisper-large-v3", "language": "ko"},
            )

        result = resp.json()
        if "text" not in result:
            return jsonify({"error": str(result)}), 500
        return jsonify({"text": result["text"]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
