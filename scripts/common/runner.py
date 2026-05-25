from __future__ import annotations

from pathlib import Path
from typing import Callable

Packet = dict[str, object]
BuildPacket = Callable[..., Packet]
WritePacket = Callable[[Path, Packet], None]


def resolve_output_path(
    *,
    repo_root: str | Path,
    out_path: str | Path | None,
    relative_out_path: Path,
) -> Path:
    if out_path is not None:
        return Path(out_path)
    return Path(repo_root) / relative_out_path


def run_packet_and_write(
    *,
    repo_root: str | Path,
    out_path: str | Path | None,
    relative_out_path: Path,
    build_packet: BuildPacket,
    write_packet: WritePacket,
) -> Packet:
    packet = build_packet(repo_root=repo_root)
    target = resolve_output_path(
        repo_root=repo_root,
        out_path=out_path,
        relative_out_path=relative_out_path,
    )
    write_packet(target, packet)
    return packet


def print_packet_fields(packet: Packet, *fields: str) -> None:
    for field in fields:
        print(packet[field])
