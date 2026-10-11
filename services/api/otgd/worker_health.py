"""Monotonic progress evidence for the actual dispatcher and SQS consumers.

A process being alive is insufficient. Each channel must have completed useful
dependency work recently; failures invalidate that channel immediately.
"""

import json
import os
from pathlib import Path
import stat
import threading
import time

CHANNELS = frozenset({"dispatcher", "cleanup", "consumer-0", "consumer-1"})
MAX_AGE_SECONDS = 75
PATH = "/tmp/otgd-worker-health.json"


def process_start(pid):
    # comm may contain spaces/parentheses; parse after its final closing bracket.
    fields = Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()
    return fields[19]


class WorkerHealth:
    def __init__(self, path=PATH, *, clock=time.monotonic_ns):
        self.path = Path(path)
        self.clock = clock
        self.lock = threading.Lock()
        self.pid = os.getpid()
        self.started = process_start(self.pid)
        self.channels = {}
        self.publish()

    def publish(self):
        data = json.dumps(
            {
                "schema_version": 1,
                "pid": self.pid,
                "process_start": self.started,
                "channels": self.channels,
            },
            separators=(",", ":"),
        ).encode()
        temporary = self.path.with_name(self.path.name + ".new")
        fd = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600
        )
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(data)
        os.replace(temporary, self.path)

    def success(self, channel):
        if channel not in CHANNELS:
            raise ValueError("Unknown worker health channel")
        with self.lock:
            self.channels[channel] = self.clock()
            self.publish()

    def failure(self, channel):
        if channel not in CHANNELS:
            raise ValueError("Unknown worker health channel")
        with self.lock:
            self.channels.pop(channel, None)
            self.publish()


def healthy(path=PATH, *, clock=time.monotonic_ns):
    try:
        file = Path(path)
        metadata = file.lstat()
        if (
            not stat.S_ISREG(metadata.st_mode)
            or metadata.st_mode & 0o077
            or metadata.st_size > 4096
        ):
            return False
        value = json.loads(file.read_bytes())
        if (
            set(value) != {"schema_version", "pid", "process_start", "channels"}
            or value["schema_version"] != 1
        ):
            return False
        if (
            type(value["pid"]) is not int
            or value["pid"] < 1
            or process_start(value["pid"]) != value["process_start"]
        ):
            return False
        if (
            not isinstance(value["channels"], dict)
            or set(value["channels"]) != CHANNELS
        ):
            return False
        tick = clock()
        return all(
            type(v) is int and 0 <= tick - v <= MAX_AGE_SECONDS * 1_000_000_000
            for v in value["channels"].values()
        )
    except (OSError, ValueError, TypeError, KeyError, IndexError):
        return False


def main():
    status = healthy()
    print("worker_progress_healthy" if status else "worker_progress_unhealthy")
    return 0 if status else 1


if __name__ == "__main__":
    raise SystemExit(main())
