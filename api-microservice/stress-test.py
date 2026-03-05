import asyncio
import aiohttp
import time
import random
import os
from dataclasses import dataclass, field
from collections import defaultdict

BASE_URL = os.getenv("BASE_URL", "http://45.55.118.71/users")

ENDPOINTS = ["/", "/live", "/ready"]

STAGES = [
    {"duration": 30, "vus": 20},
    {"duration": 60, "vus": 80},
    {"duration": 60, "vus": 150},
    {"duration": 60, "vus": 200},
    {"duration": 60, "vus": 50},
    {"duration": 30, "vus": 0},
]


@dataclass
class Stats:
    total: int = 0
    errors: int = 0
    durations: list = field(default_factory=list)
    by_endpoint: dict = field(default_factory=lambda: defaultdict(int))

    def add(self, duration_ms: float, endpoint: str, ok: bool):
        self.total += 1
        self.durations.append(duration_ms)
        self.by_endpoint[endpoint] += 1
        if not ok:
            self.errors += 1

    def report(self, stage_label: str):
        if not self.durations:
            return
        sorted_d = sorted(self.durations)
        p50 = sorted_d[int(len(sorted_d) * 0.50)]
        p95 = sorted_d[int(len(sorted_d) * 0.95)]
        p99 = sorted_d[int(len(sorted_d) * 0.99)]
        error_rate = (self.errors / self.total * 100) if self.total else 0
        rps = self.total / sum(s["duration"] for s in STAGES[:STAGES.index(
            next(s for s in STAGES if s["duration"] > 0)
        ) + 1]) if self.total else 0

        print(f"\n{'=' * 55}")
        print(f"  {stage_label}")
        print(f"{'=' * 55}")
        print(f"  Total requests : {self.total}")
        print(f"  Errores        : {self.errors} ({error_rate:.1f}%)")
        print(f"  p50 latencia   : {p50:.1f} ms")
        print(f"  p95 latencia   : {p95:.1f} ms")
        print(f"  p99 latencia   : {p99:.1f} ms")
        print(f"  Por endpoint   :")
        for ep, count in sorted(self.by_endpoint.items()):
            print(f"    {ep:<10} {count} requests")
        print(f"{'=' * 55}\n")


stats = Stats()
active_vus = 0
stop_event = asyncio.Event()


async def virtual_user(session: aiohttp.ClientSession):
    global active_vus
    active_vus += 1
    try:
        while not stop_event.is_set():
            endpoint = random.choice(ENDPOINTS)
            url = f"{BASE_URL}{endpoint}"
            start = time.perf_counter()
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    await resp.text()
                    duration_ms = (time.perf_counter() - start) * 1000
                    ok = resp.status == 200
                    stats.add(duration_ms, endpoint, ok)
            except Exception:
                duration_ms = (time.perf_counter() - start) * 1000
                stats.add(duration_ms, endpoint, ok=False)

            await asyncio.sleep(random.uniform(0, 0.5))
    finally:
        active_vus -= 1


async def run():
    print(f"\nTarget: {BASE_URL}")
    print(f"Endpoints: {ENDPOINTS}")
    print(f"Stages: {STAGES}\n")

    connector = aiohttp.TCPConnector(limit=500)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = set()
        stage_start = time.time()

        for i, stage in enumerate(STAGES):
            target_vus = stage["vus"]
            duration = stage["duration"]
            print(
                f"[Stage {i+1}/{len(STAGES)}] {target_vus} VUs durante {duration}s")

            # Ajusta VUs activos
            current = len(tasks)
            if target_vus > current:
                for _ in range(target_vus - current):
                    t = asyncio.create_task(virtual_user(session))
                    tasks.add(t)
                    t.add_done_callback(tasks.discard)
            elif target_vus < current:
                to_cancel = list(tasks)[:current - target_vus]
                for t in to_cancel:
                    t.cancel()

            elapsed = 0
            while elapsed < duration:
                await asyncio.sleep(10)
                elapsed += 10
                rps = stats.total / max(time.time() - stage_start, 1)
                err_rate = (stats.errors / stats.total *
                            100) if stats.total else 0
                print(f"  t={int(time.time()-stage_start)}s | VUs={len(tasks)} | "
                      f"req={stats.total} | rps={rps:.1f} | errors={err_rate:.1f}%")

        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)

    stats.report("RESULTADO FINAL")


if __name__ == "__main__":
    asyncio.run(run())
