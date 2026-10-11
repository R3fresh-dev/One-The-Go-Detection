import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from otgd import worker_health as h


def test_no_startup_success_until_each_actual_loop_has_completed(tmp_path):
    clock = [100_000_000_000]
    path = tmp_path / "health.json"
    health = h.WorkerHealth(path, clock=lambda: clock[0])
    assert not h.healthy(path, clock=lambda: clock[0])
    for channel in h.CHANNELS:
        health.success(channel)
    assert h.healthy(path, clock=lambda: clock[0])
    clock[0] += 75_000_000_000
    assert h.healthy(path, clock=lambda: clock[0])
    clock[0] += 1
    assert not h.healthy(path, clock=lambda: clock[0])
    for channel in h.CHANNELS:
        health.success(channel)
    assert h.healthy(path, clock=lambda: clock[0])
    health.failure("consumer-1")
    assert not h.healthy(path, clock=lambda: clock[0])
    health.success("consumer-1")
    assert h.healthy(path, clock=lambda: clock[0])


def test_parallel_progress_updates_do_not_lose_consumers(tmp_path):
    path = tmp_path / "health"
    health = h.WorkerHealth(path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(health.success, list(h.CHANNELS) * 10))
    assert h.healthy(path)
    assert path.stat().st_mode & 0o077 == 0
    for operation in (health.success, health.failure):
        with pytest.raises(ValueError):
            operation("unknown")


@pytest.mark.parametrize(
    "changes",
    [
        dict(pid=True),
        dict(pid=0),
        dict(process_start="wrong"),
        dict(channels={}),
        dict(channels={k: True for k in h.CHANNELS}),
        dict(channels={k: 999_000_000_000 for k in h.CHANNELS}),
        dict(schema_version=2),
        dict(extra="field"),
    ],
)
def test_pid_reuse_malformed_and_future_progress_fail_closed(tmp_path, changes):
    path = tmp_path / "health"
    health = h.WorkerHealth(path, clock=lambda: 100)
    for channel in h.CHANNELS:
        health.success(channel)
    value = json.loads(path.read_bytes())
    value.update(changes)
    path.write_text(json.dumps(value))
    assert not h.healthy(path, clock=lambda: 100)


def test_missing_symlink_exposed_oversized_and_invalid_state_fail_closed(tmp_path):
    path = tmp_path / "health"
    assert not h.healthy(path)
    path.write_text("invalid")
    path.chmod(0o600)
    assert not h.healthy(path)
    path.write_text("x" * 4097)
    assert not h.healthy(path)
    path.chmod(0o644)
    assert not h.healthy(path)
    link = tmp_path / "link"
    link.symlink_to(path)
    assert not h.healthy(link)


def test_health_command_returns_status_only(monkeypatch, capsys):
    monkeypatch.setattr(h, "healthy", lambda: False)
    assert (
        h.main() == 1 and capsys.readouterr().out.strip() == "worker_progress_unhealthy"
    )
    monkeypatch.setattr(h, "healthy", lambda: True)
    assert (
        h.main() == 0 and capsys.readouterr().out.strip() == "worker_progress_healthy"
    )


def test_sqs_poll_success_records_progress_and_outage_invalidates_it(
    tmp_path, monkeypatch
):
    from otgd import worker
    import threading

    health = h.WorkerHealth(tmp_path / "health")
    for channel in h.CHANNELS:
        health.success(channel)
    event = threading.Event()
    monkeypatch.setattr(worker, "stop", event)

    class Queue:
        failure = False

        def receive_message(self, **kwargs):
            event.set()
            if self.failure:
                raise ConnectionError("synthetic dependency outage")
            return {"Messages": []}

    queue = Queue()
    monkeypatch.setattr(worker.storage, "client", lambda _: queue)
    worker.consume(health, "consumer-0")
    assert h.healthy(health.path)
    event.clear()
    queue.failure = True
    worker.consume(health, "consumer-0")
    assert not h.healthy(health.path)
