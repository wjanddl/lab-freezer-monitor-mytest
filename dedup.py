"""Remove duplicate emails from a one-per-line text file, in place."""
import os
import shutil
import sys
import tempfile


def dedup(lines):
    seen = set()
    out = []
    for line in lines:
        email = line.strip()
        key = email.casefold()
        if email and key not in seen:
            seen.add(key)
            out.append(email)
    return out


def main(argv):
    if len(argv) != 2:
        print("usage: python dedup.py FILE", file=sys.stderr)
        return 2
    path = argv[1]
    try:
        with open(path, encoding="utf-8-sig") as f:
            lines = f.read().splitlines()
    except OSError as e:
        print("error: {}".format(e), file=sys.stderr)
        return 1

    kept = dedup(lines)
    removed = len(lines) - len(kept)

    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)))
    try:
        with open(fd, "w", encoding="utf-8", newline="\n") as f:
            f.writelines(email + "\n" for email in kept)
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise

    print("kept {}, removed {}".format(len(kept), removed), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
