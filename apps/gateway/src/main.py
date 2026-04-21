"""Entry point for the gateway daemon.

Loads config, builds the DI container, starts the runtime, and runs forever
until a SIGINT/SIGTERM arrives.
"""

from __future__ import annotations

import asyncio
import signal

from config import GatewayConfig
from container import build_container
from logger import Logger


async def run() -> None:
    logger = Logger("gateway.main")
    config = GatewayConfig()
    container = build_container(config)

    await container.gateway_runtime_service.start()

    stop_event = asyncio.Event()

    def request_stop() -> None:
        logger.info("signal received; stopping")
        stop_event.set()

    asyncio_loop = asyncio.get_running_loop()
    for signal_name in ("SIGINT", "SIGTERM"):
        signal_value = getattr(signal, signal_name, None)
        if signal_value is None:
            continue
        try:
            asyncio_loop.add_signal_handler(signal_value, request_stop)
        except NotImplementedError:
            # Windows asyncio doesn't support add_signal_handler.
            pass

    try:
        await stop_event.wait()
    finally:
        await container.gateway_runtime_service.stop()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
