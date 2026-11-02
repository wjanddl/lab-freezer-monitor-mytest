import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dedup.py")


def run(*args):
    return subprocess.run([sys.executable, SCRIPT] + list(args),
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)


with tempfile.TemporaryDirectory() as d:
    p = os.path.join(d, "emails.txt")

    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write("a@x.com\n A@X.com \n\nb@y.com\nnot-an-email\nb@y.com\n")
    r = run(p)
    assert r.returncode == 0, r.stderr
    with open(p, encoding="utf-8", newline="") as f:
        assert f.read() == "a@x.com\nb@y.com\nnot-an-email\n"
    assert b"kept 3, removed 3" in r.stderr, r.stderr

    with open(p, "w", encoding="utf-8-sig") as f:
        f.write("a@x.com\r\nA@x.com\r\n")
    assert run(p).returncode == 0
    with open(p, "rb") as f:
        assert f.read() == b"a@x.com\n"

    assert os.listdir(d) == ["emails.txt"]  # no temp file left behind
    assert run(os.path.join(d, "missing.txt")).returncode != 0
    assert run().returncode != 0

print("OK")
