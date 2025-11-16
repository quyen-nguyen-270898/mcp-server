from flask import Flask, Response, request
import subprocess
import yt_dlp

app = Flask(__name__)

def get_audio_url(video_url):
    opts = {"format": "bestaudio", "quiet": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info["url"]

@app.route("/stream")
def stream():
    url = request.args.get("url")
    if not url:
        return "Missing url", 400

    audio = get_audio_url(url)

    cmd = [
        "ffmpeg",
        "-i", audio,
        "-f", "mp3",
        "-ac", "2",
        "-ar", "44100",
        "-"
    ]

    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )

    return Response(process.stdout, mimetype="audio/mpeg")

@app.route("/")
def home():
    return "MCP YouTube stream server OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
