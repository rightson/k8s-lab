"""Tests only shell guard control flow using local fixtures, not a cluster."""
import os, shutil, subprocess, tempfile, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class GuardTests(unittest.TestCase):
    def test_no_marker_stops_before_kubectl(self):
        p = subprocess.run(["bash", str(ROOT/"src/cluster.sh"), "status"],
                           capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertIn("No owned cluster marker", p.stderr)

    def test_unpinned_image_rejected_without_docker(self):
        p = subprocess.run(["bash", str(ROOT/"src/cluster.sh"), "create",
                            "--confirm-isolated", "python:latest"],
                            capture_output=True, text=True, timeout=5)
        self.assertEqual(p.returncode, 2)
        self.assertIn("digest-pinned", p.stderr)

    def test_mismatched_uid_stops_before_mutation(self):
        with tempfile.TemporaryDirectory(prefix="k082-guard-") as directory:
            base = Path(directory)
            (base/"src").mkdir()
            (base/".private").mkdir()
            (base/"bin").mkdir()
            shutil.copyfile(ROOT/"src/cluster.sh", base/"src/cluster.sh")
            # Fixtures contain no real credentials.
            (base/".private/kubeconfig").write_text("TEST FIXTURE ONLY")
            (base/".private/cluster-uid").write_text("expected-test-uid")
            fake = base/"bin/kubectl"
            fake.write_text("#!/bin/sh\nprintf 'different-test-uid'\n")
            fake.chmod(0o700)
            p = subprocess.run(["bash", str(base/"src/cluster.sh"), "cleanup",
                                "--confirm-isolated"],
                env={**os.environ, "PATH": str(base/"bin")+os.pathsep+os.environ["PATH"]},
                capture_output=True, text=True, timeout=5)
            self.assertEqual(p.returncode, 2)
            self.assertIn("Cluster UID mismatch", p.stderr)
            self.assertTrue((base/".private/kubeconfig").exists())

if __name__ == "__main__":
    unittest.main(verbosity=2)

