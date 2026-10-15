"""Python HTTP and static-intent tests only. These do NOT test Kubernetes."""
import importlib.util, json, os, queue, subprocess, sys, threading, unittest
import urllib.error, urllib.request
from pathlib import Path
import yaml
ROOT = Path(__file__).resolve().parents[1]

class Process:
    def __init__(self, **env):
        self.proc = subprocess.Popen([sys.executable, "-u", str(ROOT / "src/api.py")],
            env={**os.environ, "BIND": "127.0.0.1", "PORT": "0", **env},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        incoming = queue.Queue()
        threading.Thread(target=lambda: incoming.put(self.proc.stdout.readline()), daemon=True).start()
        self.port = json.loads(incoming.get(timeout=5))["listening"]
    def call(self, path, post=False):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}", method="POST" if post else "GET")
        try:
            with urllib.request.urlopen(req, timeout=3) as r: return r.status, json.load(r)
        except urllib.error.HTTPError as r: return r.code, json.load(r)
    def close(self):
        if self.proc.poll() is None: self.proc.terminate()
        self.proc.communicate(timeout=5)

class OfflineTests(unittest.TestCase):
    def setUp(self): self.ps = []
    def process(self, **env):
        p = Process(**env); self.ps.append(p); return p
    def tearDown(self):
        for p in self.ps: p.close()
    def test_identity(self):
        code, b = self.process(POD_NAME="sample", POD_UID="uid-test").call("/id")
        self.assertEqual((code, b["pod"], b["uid"]), (200, "sample", "uid-test"))
    def test_readiness_does_not_kill_process(self):
        p = self.process(ALLOW_FAULTS="1")
        self.assertEqual(p.call("/admin/not-ready", True)[0], 200)
        self.assertEqual(p.call("/readyz")[0], 503)
        self.assertEqual(p.call("/healthz")[0], 200)
        p.call("/admin/ready", True)
        self.assertEqual(p.call("/readyz")[0], 200)
    def test_bad_version_readiness_flag(self):
        self.assertEqual(self.process(FAIL_READINESS="1").call("/readyz")[0], 503)
    def test_faults_disabled(self):
        self.assertEqual(self.process(ALLOW_FAULTS="0").call("/admin/crash", True)[0], 403)
    def test_counter_not_shared(self):
        a, b = self.process(), self.process()
        a.call("/increment", True)
        self.assertEqual(a.call("/id")[1]["count"], 1)
        self.assertEqual(b.call("/id")[1]["count"], 0)
    def test_exit_and_volatile_state_loss(self):
        p = self.process(ALLOW_FAULTS="1")
        p.call("/increment", True)
        self.assertEqual(p.call("/admin/crash", True)[0], 202)
        self.assertEqual(p.proc.wait(timeout=5), 17)
        self.assertEqual(self.process().call("/id")[1]["count"], 0)
    def test_unknown(self):
        self.assertEqual(self.process().call("/missing")[0], 404)
    def test_manifest_intent(self):
        ns, dep, svc = list(yaml.safe_load_all((ROOT / "manifests/app.yaml").read_text()))
        self.assertEqual(ns["metadata"]["name"], "k082-foundations")
        self.assertEqual(dep["spec"]["replicas"], 2)
        labels = dep["spec"]["template"]["metadata"]["labels"]
        self.assertEqual(dep["spec"]["selector"]["matchLabels"], labels)
        self.assertEqual(svc["spec"]["selector"], labels)
        self.assertFalse(dep["spec"]["template"]["spec"]["automountServiceAccountToken"])
        self.assertEqual(dep["spec"]["strategy"]["rollingUpdate"], {"maxUnavailable": 0, "maxSurge": 1})
    def test_render_rejects_unbuilt_image(self):
        spec = importlib.util.spec_from_file_location("render", ROOT / "src/render.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        for bad in ("k082-api:unbuilt", "k082-api:latest", "nginx:latest"):
            with self.assertRaises(ValueError): mod.render(bad)
        docs = list(yaml.safe_load_all(mod.render("k082-api:" + "a"*12)))
        self.assertEqual(docs[1]["spec"]["replicas"], 2)

if __name__ == "__main__": unittest.main(verbosity=2)

