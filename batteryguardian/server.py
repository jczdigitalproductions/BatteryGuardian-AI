"""Local-only offline dashboard. No remote APIs or third-party dependencies."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import json
import logging
from .core import parse_csv, analyze

ROOT = Path(__file__).resolve().parent.parent
MAX_BODY = 2_000_000

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/':
            data = (ROOT / 'batteryguardian' / 'index.html').read_bytes()
            self.reply(200, data, 'text/html; charset=utf-8')
        elif route == '/app.js':
            self.reply(200, (ROOT / 'batteryguardian' / 'app.js').read_bytes(), 'text/javascript; charset=utf-8')
        elif route == '/api/demo':
            text = (ROOT / 'data' / 'demo.csv').read_text(encoding='utf-8')
            samples = parse_csv(text)
            result = analyze(samples)
            checkpoint = ROOT / 'artifacts' / 'battery_model.pt'
            if checkpoint.is_file() and len(samples) >= 8:
                try:
                    from ml.infer import infer
                    result['ml_advisory'] = infer(samples, str(checkpoint))
                except (ImportError, RuntimeError, ValueError, OSError) as exc:
                    result['ml_advisory_error'] = str(exc)
            self.reply(200, json.dumps(result).encode(), 'application/json')
        elif route == '/health':
            self.reply(200, b'{"status":"ok","offline":true}', 'application/json')
        else:
            self.reply(404, b'Not found')

    def do_POST(self):
        if urlparse(self.path).path != '/api/analyze':
            return self.reply(404, b'Not found')
        length = self.headers.get('Content-Length', '')
        if not length.isdigit() or int(length) > MAX_BODY:
            return self.reply(413, b'{"error":"Body missing or too large"}', 'application/json')
        try:
            raw = self.rfile.read(int(length)).decode('utf-8')
            samples = parse_csv(raw)
            result = analyze(samples)
            # Advisory model never modifies deterministic safety status.
            checkpoint = ROOT / 'artifacts' / 'battery_model.pt'
            if checkpoint.is_file() and len(samples) >= 8:
                try:
                    from ml.infer import infer
                    result['ml_advisory'] = infer(samples, str(checkpoint))
                except (ImportError, RuntimeError, ValueError, OSError) as exc:
                    result['ml_advisory_error'] = str(exc)
            self.reply(200, json.dumps(result).encode(), 'application/json')
        except (UnicodeError, ValueError) as exc:
            self.reply(400, json.dumps({'error': str(exc)}).encode(), 'application/json')

    def reply(self, status, data, content_type='text/plain; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(data)


def main():
    logging.basicConfig(level=logging.INFO)
    host, port = '127.0.0.1', 8765
    print(f'BatteryGuardian: http://{host}:{port} (localhost only)', flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()

if __name__ == '__main__':
    main()
