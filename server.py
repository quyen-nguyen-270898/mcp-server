"""Simple YouTube search microservice.

Provides /search endpoint returning metadata (videoId, title, thumbnails, watchUrl, embedUrl)
and DOES NOT attempt to bypass YouTube anti‑bot or extract raw audio stream URLs that would
violate YouTube Terms of Service. To play audio, use the official watch or embed URL client-side.

Environment variables:
  YOUTUBE_API_KEY  (required) Your YouTube Data API v3 key.
  PORT             (optional) Port to bind, default 5000.

Run: python server.py
"""

import os
import logging
from typing import List, Dict, Any
from flask import Flask, request, jsonify, send_file, abort
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("youtube-search-service")

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
	logger.warning("YOUTUBE_API_KEY not set – /search will return 500 until provided.")

def youtube_search(q: str, max_results: int = 5) -> List[Dict[str, Any]]:
	"""Call YouTube Data API to search videos by query string.

	Returns a list of result dicts containing videoId, title, thumbnails, watchUrl, embedUrl.
	"""
	service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
	logger.info("Executing YouTube search: '%s' (max=%d)", q, max_results)
	response = service.search().list(
		q=q,
		part="snippet",
		type="video",
		maxResults=max_results,
		safeSearch="none",
	).execute()

	results = []
	for item in response.get("items", []):
		vid = item["id"].get("videoId")
		snippet = item.get("snippet", {})
		if not vid:
			continue
		results.append({
			"videoId": vid,
			"title": snippet.get("title"),
			"description": snippet.get("description"),
			"channelTitle": snippet.get("channelTitle"),
			"publishedAt": snippet.get("publishedAt"),
			"thumbnails": snippet.get("thumbnails", {}),
			"watchUrl": f"https://www.youtube.com/watch?v={vid}",
			"embedUrl": f"https://www.youtube.com/embed/{vid}",
		})
	return results

@app.get("/health")
def health() -> Any:
	return {"status": "ok"}

@app.get("/search")
def search() -> Any:
	if not YOUTUBE_API_KEY:
		return jsonify({"error": "Server missing YOUTUBE_API_KEY"}), 500

	query = request.args.get("query", "").strip()
	if not query:
		return jsonify({"error": "Missing query parameter 'query'"}), 400
	if len(query) > 200:
		return jsonify({"error": "Query too long"}), 400

	max_results_raw = request.args.get("max", "5")
	try:
		max_results = int(max_results_raw)
	except ValueError:
		return jsonify({"error": "Invalid max parameter"}), 400
	if not (1 <= max_results <= 25):
		return jsonify({"error": "max must be between 1 and 25"}), 400

	try:
		items = youtube_search(query, max_results=max_results)
	except HttpError as e:
		logger.exception("YouTube API error")
		return jsonify({"error": "YouTube API error", "details": str(e)}), 502
	except Exception as e:  # noqa: BLE001 keep broad for a small service
		logger.exception("Unexpected error during search")
		return jsonify({"error": "Internal error", "details": str(e)}), 500

	lite = request.args.get("lite", "false").lower() in {"1", "true", "yes"}
	if lite:
		lite_items = [
			{
				"videoId": i["videoId"],
				"title": i["title"],
				"embedUrl": i["embedUrl"],
			}
			for i in items
		]
		return jsonify({
			"query": query,
			"count": len(lite_items),
			"results": lite_items,
			"mode": "lite",
			"note": "Lite mode: only identifiers and embed URL returned."
		})

	return jsonify({
		"query": query,
		"count": len(items),
		"results": items,
		"mode": "full",
		"note": "Use watchUrl or embedUrl client-side. Direct audio stream URLs are intentionally not exposed to comply with YouTube Terms of Service."
	})

@app.get("/play")
def play() -> Any:
	"""Return minimal embed metadata for a given videoId.

	Client can embed via IFrame: <iframe src=embedUrl allow="autoplay"></iframe>
	This avoids scraping or attempting to obtain raw audio stream URLs.
	"""
	if not YOUTUBE_API_KEY:
		return jsonify({"error": "Server missing YOUTUBE_API_KEY"}), 500
	video_id = request.args.get("videoId", "").strip()
	if not video_id:
		return jsonify({"error": "Missing videoId parameter"}), 400

	# Fetch snippet for single video to get title (Videos.list endpoint)
	try:
		service = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
		resp = service.videos().list(part="snippet", id=video_id).execute()
		items = resp.get("items", [])
		if not items:
			return jsonify({"error": "videoId not found"}), 404
		snippet = items[0].get("snippet", {})
		data = {
			"videoId": video_id,
			"title": snippet.get("title"),
			"embedUrl": f"https://www.youtube.com/embed/{video_id}",
			"watchUrl": f"https://www.youtube.com/watch?v={video_id}",
			"thumbnails": snippet.get("thumbnails", {}),
			"channelTitle": snippet.get("channelTitle"),
			"note": "Provide embedUrl to client. Do not request raw audio stream URLs.",
		}
		return jsonify(data)
	except HttpError as e:
		logger.exception("YouTube API error while /play")
		return jsonify({"error": "YouTube API error", "details": str(e)}), 502
	except Exception as e:  # noqa: BLE001
		logger.exception("Unexpected error during /play")
		return jsonify({"error": "Internal error", "details": str(e)}), 500

# Audio file serving (user-provided lawful audio files)
ALLOWED_AUDIO_EXT = {".mp3", ".ogg", ".wav", ".m4a"}
AUDIO_DIR = os.getenv("AUDIO_DIR", os.path.join(os.getcwd(), "audio"))

def _list_audio_files() -> List[Dict[str, Any]]:
	if not os.path.isdir(AUDIO_DIR):
		return []
	entries: List[Dict[str, Any]] = []
	for name in os.listdir(AUDIO_DIR):
		lower = name.lower()
		ext = os.path.splitext(lower)[1]
		if ext in ALLOWED_AUDIO_EXT:
			file_id = os.path.splitext(name)[0]
			entries.append({
				"id": file_id,
				"filename": name,
				"streamUrl": f"/stream/{file_id}",
			})
	return sorted(entries, key=lambda x: x["id"])

@app.get("/tracks")
def tracks() -> Any:
	"""List available audio tracks stored in AUDIO_DIR.

	Only exposes user-provided files; does not fetch or transcode YouTube.
	"""
	items = _list_audio_files()
	return jsonify({
		"count": len(items),
		"results": items,
		"note": "Files served are user-provided. No YouTube raw stream extraction performed.",
	})

@app.get("/stream/<track_id>")
def stream(track_id: str) -> Any:
	"""Serve a single audio file by its id (filename without extension).

	Path sanitization prevents directory traversal. Only whitelisted extensions are served.
	ESP32 can consume via simple HTTP GET progressive download.
	"""
	if not track_id:
		return jsonify({"error": "Missing track id"}), 400
	if any(ch in track_id for ch in ("/", "\\", "..")):
		return jsonify({"error": "Invalid track id"}), 400
	if not os.path.isdir(AUDIO_DIR):
		return jsonify({"error": "Audio directory not found"}), 404
	# Find matching file with allowed extension
	for name in os.listdir(AUDIO_DIR):
		base, ext = os.path.splitext(name)
		if base == track_id and ext.lower() in ALLOWED_AUDIO_EXT:
			file_path = os.path.join(AUDIO_DIR, name)
			mimetype = "audio/mpeg" if ext.lower() == ".mp3" else (
				"audio/ogg" if ext.lower() == ".ogg" else (
					"audio/wav" if ext.lower() == ".wav" else "audio/mp4"
				)
			)
			try:
				return send_file(file_path, mimetype=mimetype, conditional=True)
			except FileNotFoundError:
				abort(404)
	return jsonify({"error": "Track not found"}), 404

def main() -> None:
	port = int(os.getenv("PORT", "5000"))
	host = "0.0.0.0"
	logger.info("Starting server on %s:%d", host, port)
	app.run(host=host, port=port)

if __name__ == "__main__":
	main()
