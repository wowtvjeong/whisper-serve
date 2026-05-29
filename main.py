from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)
CORS(app)

def extract_video_id(url):
    patterns = [r'v=([^&]+)', r'youtu\.be/([^?]+)', r'shorts/([^?]+)']
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/transcribe", methods=["POST"])
def transcribe():
    data = request.json
    url  = data.get("url", "")
    if not url:
        return jsonify({"error": "URL이 필요합니다"}), 400

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({"error": "유튜브 URL을 확인해주세요"}), 400

    try:
        transcript = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["ko", "en"]
        )
        text = " ".join([t["text"] for t in transcript])
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"error": f"자막을 찾을 수 없어요: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
