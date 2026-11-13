"""Loopback-only TCP bridges from Docker Desktop to approved AINPC VPN endpoints."""

from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from functools import partial


LISTEN_HOST = "127.0.0.1"
CONNECT_TIMEOUT_SECONDS = 8.0
BRIDGES = (
    ("ragflow", 8000, "172.24.131.150", 8000),
    ("input-precheck", 8040, "172.24.140.71", 8040),
    ("loongeq", 8041, "172.24.140.71", 8041),
    ("sensitive-word", 8090, "14.103.105.119", 8040),
    ("loongmemory", 8230, "172.24.140.71", 8230),
    ("loongmemory-console", 8231, "172.24.140.71", 8231),
    ("exact-search", 10010, "172.24.140.24", 10010),
)


def emit(event: str, **fields: object) -> None:
    print(json.dumps({"event": event, **fields}, ensure_ascii=True), flush=True)


async def relay(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
    try:
        while data := await reader.read(64 * 1024):
            writer.write(data)
            await writer.drain()
    except (ConnectionError, asyncio.CancelledError):
        pass
    finally:
        with suppress(ConnectionError, RuntimeError):
            writer.write_eof()


async def handle_client(
    client_reader: asyncio.StreamReader,
    client_writer: asyncio.StreamWriter,
    *,
    name: str,
    upstream_host: str,
    upstream_port: int,
) -> None:
    upstream_writer: asyncio.StreamWriter | None = None
    try:
        upstream_reader, upstream_writer = await asyncio.wait_for(
            asyncio.open_connection(upstream_host, upstream_port),
            timeout=CONNECT_TIMEOUT_SECONDS,
        )
        await asyncio.gather(
            relay(client_reader, upstream_writer),
            relay(upstream_reader, client_writer),
        )
    except (OSError, TimeoutError) as error:
        emit("upstream_unavailable", bridge=name, error_type=type(error).__name__)
    finally:
        client_writer.close()
        with suppress(Exception):
            await client_writer.wait_closed()
        if upstream_writer is not None:
            upstream_writer.close()
            with suppress(Exception):
                await upstream_writer.wait_closed()


async def main() -> None:
    servers: list[asyncio.AbstractServer] = []
    try:
        for name, listen_port, upstream_host, upstream_port in BRIDGES:
            server = await asyncio.start_server(
                partial(
                    handle_client,
                    name=name,
                    upstream_host=upstream_host,
                    upstream_port=upstream_port,
                ),
                LISTEN_HOST,
                listen_port,
                reuse_address=True,
            )
            servers.append(server)
            emit(
                "proxy_ready",
                bridge=name,
                listen_host=LISTEN_HOST,
                listen_port=listen_port,
                upstream_host=upstream_host,
                upstream_port=upstream_port,
            )
        await asyncio.gather(*(server.serve_forever() for server in servers))
    finally:
        for server in servers:
            server.close()
        await asyncio.gather(
            *(server.wait_closed() for server in servers),
            return_exceptions=True,
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
