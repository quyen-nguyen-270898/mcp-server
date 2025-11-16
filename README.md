# SoundCloud Stream URL Extractor

Web service to extract audio stream URLs from SoundCloud tracks.

## Features

- Extract direct audio stream links from SoundCloud URLs
- Get track metadata (title, artist, duration, thumbnail)
- Optional API key authentication
- Simple REST API

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure if needed:
```bash
cp .env.example .env
```

3. Run the server:
```bash
python server.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### GET `/`
Health check and usage information

### GET `/health`
Health status for monitoring/deployment

### POST `/stream`
Extract audio stream URL from SoundCloud

**Request body:**
```json
{
  "url": "https://soundcloud.com/user/track-name"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "stream_url": "https://...",
  "title": "Track Title",
  "artist": "Artist Name",
  "duration": 180,
  "thumbnail": "https://...",
  "ext": "m4a"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Error message"
}
```

### Example Usage

```bash
curl -X POST http://localhost:5000/stream \
  -H "Content-Type: application/json" \
  -d '{"url":"https://soundcloud.com/user/track-name"}'
```

With API key:
```bash
curl -X POST "http://localhost:5000/stream?key=your_api_key" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://soundcloud.com/user/track-name"}'
```

## Deployment on Render

1. Create new Web Service on Render
2. Connect your GitHub repository
3. Configure environment:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn server:app`
   - **Runtime:** Python 3.11

4. Set environment variables:
   - `API_KEY` (optional): Your API key for authentication

5. Deploy!

The Procfile is already configured for Render deployment.

## Security

- Enable API key authentication by setting `API_KEY` environment variable
- Use HTTPS in production (Render provides SSL automatically)
- Add rate limiting for production use (implement in future versions)

## Troubleshooting

- **"yt-dlp not found"**: Make sure it's installed: `pip install yt-dlp`
- **Timeout errors**: Some SoundCloud tracks may take longer to extract
- **Invalid URL**: Ensure the URL is a valid SoundCloud link

## Notes

- Stream URLs may have expiration times (usually hours)
- Respect SoundCloud's terms of service
- Use responsibly and don't overload the service
