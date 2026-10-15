"""Disposable teaching API, not a production service."""
import json, os, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args): pass

    def reply(self, code, body):
        payload = json.dumps(body, sort_keys=True).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(payload)
        self.wfile.flush()

    def do_GET(self):
        with self.server.lock:
            count, ready = self.server.count, self.server.ready
        if self.path == "/healthz":
            self.reply(200, {"alive": True})
        elif self.path == "/readyz":
            self.reply(200 if ready else 503, {"ready": ready})
        elif self.path == "/id":
            self.reply(200, {"pod": os.getenv("POD_NAME", "local"),
                "uid": os.getenv("POD_UID", "local"),
                "version": os.getenv("VERSION", "v1"), "count": count})
        else:
            self.reply(404, {"error": "unknown route"})

    def do_POST(self):
        if self.path == "/increment":
            with self.server.lock:
                self.server.count += 1
                count = self.server.count
            self.reply(200, {"count": count})
        elif os.getenv("ALLOW_FAULTS", "0") != "1":
            self.reply(403, {"error": "fault injection disabled"})
        elif self.path in ("/admin/not-ready", "/admin/ready"):
            with self.server.lock:
                self.server.ready = self.path == "/admin/ready"
            self.reply(200, {"ready": self.server.ready})
        elif self.path == "/admin/crash":
            self.reply(202, {"exit_code": 17})
            os._exit(17)
        else:
            self.reply(404, {"error": "unknown route"})

if __name__ == "__main__":
    server = ThreadingHTTPServer((os.getenv("BIND", "0.0.0.0"), int(os.getenv("PORT", "8080"))), Handler)
    server.lock = threading.Lock()
    server.count = 0
    server.ready = os.getenv("FAIL_READINESS", "0") != "1"
    print(json.dumps({"listening": server.server_address[1]}), flush=True)
    server.serve_forever()

