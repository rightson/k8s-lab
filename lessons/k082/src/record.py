"""Record a non-secret experiment command. Never use with credentials/config views."""
import argparse, json, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command: parser.error("command required")
    started = datetime.now(timezone.utc).isoformat()
    try:
        p = subprocess.run(command, capture_output=True, text=True, timeout=240, check=False)
        code, out, err = p.returncode, p.stdout, p.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        code, out, err = 124, "", str(exc)
    record = {"started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "argv": command, "exit_code": code, "stdout": out, "stderr": err}
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(out, end="")
    print(err, end="", file=sys.stderr)
    return code

if __name__ == "__main__":
    sys.exit(main())

