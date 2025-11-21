# YouTube Search & Local Audio Stream Service

This service provides two groups of functionality:

1. YouTube search metadata (no raw audio stream extraction).
2. Streaming of user-provided lawful audio files for embedded devices (e.g. ESP32).

## Endpoints

### Health
`GET /health` – Basic uptime check.

### YouTube Search
`GET /search?query=...&max=5&lite=true`
- Returns video metadata (videoId, title, thumbnails, watchUrl, embedUrl).
- `lite=true` reduces payload to only `videoId`, `title`, `embedUrl`.

### YouTube Single Video Metadata
`GET /play?videoId=VIDEO_ID`
- Returns minimal metadata for embedding.
- Use an `<iframe>` with the `embedUrl` on a client that can render HTML.

### List Local Audio Tracks
`GET /tracks`
- Scans `AUDIO_DIR` (default: `./audio`) for files with extensions: `.mp3`, `.ogg`, `.wav`, `.m4a`.
- Returns JSON with `id` and `streamUrl` for each track.

### Stream Local Audio Track
`GET /stream/<id>`
- Serves the matching audio file (`id` = filename without extension).
- Appropriate MIME type set (audio/mpeg, audio/ogg, audio/wav, audio/mp4).
- Intended for devices like ESP32 performing progressive HTTP reads.

## Environment Variables
`YOUTUBE_API_KEY` – Required for YouTube Data API search/play endpoints.
`PORT` – Server port (default 5000).
`AUDIO_DIR` – Directory containing your audio files (default `./audio`).

## Running Locally
```bash
export YOUTUBE_API_KEY=YOUR_KEY
mkdir -p audio
# Place demo1.mp3 (lawful file) into audio/demo1.mp3
pip install -r requirements.txt
python server.py
```

Test:
```bash
curl "http://localhost:5000/search?query=lofi&lite=true"
curl "http://localhost:5000/tracks"
curl "http://localhost:5000/stream/demo1" --output demo1.mp3
```

## ESP32 Consumption (Pseudo-Code)
```c
// Using esp_http_client to stream MP3
esp_http_client_config_t config = {
    .url = "http://your-domain/stream/demo1",
    .method = HTTP_METHOD_GET,
};
esp_http_client_handle_t client = esp_http_client_init(&config);
esp_http_client_open(client, 0);
int read;
while ((read = esp_http_client_read(client, (char*)buffer, BUFFER_SIZE)) > 0) {
    // feed buffer to audio decoder / I2S
}
esp_http_client_cleanup(client);
```

## Compliance & Limitations
- Service does NOT expose raw YouTube audio stream URLs (DASH/HLS) to comply with Terms of Service.
- All audio served via `/stream` must be files you have the rights to distribute.
- Attempting to add YouTube media extraction code is discouraged and may lead to blocking or legal issues.

## Extending
- Add simple auth (e.g. bearer token) by checking headers in `/stream`.
- Add rate limiting or caching for search responses.
- Add metadata JSON alongside audio files (e.g. `demo1.json`).

## License
No license headers were added. Provide one if you plan to open source.
