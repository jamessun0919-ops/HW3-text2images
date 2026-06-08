import http.server
import urllib.request
import urllib.parse
import json
import os

API_URL = 'https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell'
PORT = 3000
STATIC_DIR = os.path.dirname(os.path.abspath(__file__))


def translate_to_english(text):
    # Check if string contains Chinese characters
    if not any('\u4e00' <= char <= '\u9fff' for char in text):
        return text
    try:
        url = f"https://api.mymemory.translated.net/get?q={urllib.parse.quote(text)}&langpair=zh-TW|en"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode('utf-8'))
        translated = data['responseData']['translatedText']
        if translated:
            return translated
    except Exception as e:
        print(f"Translation failed: {e}")
    return text


class ProxyHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        file_path = os.path.join(STATIC_DIR, self.path.lstrip('/'))
        if os.path.isfile(file_path):
            ext = os.path.splitext(file_path)[1]
            content_types = {
                '.html': 'text/html; charset=utf-8',
                '.css': 'text/css',
                '.js': 'application/javascript',
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.svg': 'image/svg+xml',
            }
            ctype = content_types.get(ext, 'application/octet-stream')
            self.send_response(200)
            self.send_header('Content-Type', ctype)
            self.end_headers()
            with open(file_path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_POST(self):
        if self.path == '/api/generate':
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            auth = self.headers.get('Authorization', '')

            # Translate Chinese prompt if needed
            try:
                payload = json.loads(body.decode('utf-8'))
                prompt = payload.get('inputs', '')
                if prompt:
                    translated_prompt = translate_to_english(prompt)
                    if translated_prompt != prompt:
                        payload['inputs'] = translated_prompt
                        body = json.dumps(payload).encode('utf-8')
                        print(f"Translated prompt: '{prompt}' -> '{translated_prompt}'")
            except Exception as e:
                print(f"Translation processing failed: {e}")

            req = urllib.request.Request(
                API_URL,
                data=body,
                headers={
                    'Authorization': auth,
                    'Content-Type': 'application/json',
                },
                method='POST',
            )
            try:
                resp = urllib.request.urlopen(req, timeout=120)
                img_data = resp.read()
                self.send_response(200)
                self.send_header('Content-Type', resp.headers.get('Content-Type', 'image/png'))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(img_data)
            except urllib.error.HTTPError as e:
                err_body = e.read()
                self.send_response(e.code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(err_body)
            except urllib.error.URLError as e:
                self.send_response(502)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e.reason)}).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'404 Not Found')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()


if __name__ == '__main__':
    server = http.server.HTTPServer(('127.0.0.1', PORT), ProxyHandler)
    print(f'Server running at http://127.0.0.1:{PORT}')
    print('Press Ctrl+C to stop')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
