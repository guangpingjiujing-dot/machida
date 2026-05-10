from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html = "<h1>Hello from Docker!</h1><p>コンテナの中からこんにちは！</p>"
        self.wfile.write(html.encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[アクセス] {args[0]}")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("サーバー起動中: http://localhost:8000")
    server.serve_forever()
