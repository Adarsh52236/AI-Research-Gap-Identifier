"""File utilities."""
import os
import re
import hashlib
from pathlib import Path

def ensure_dir(path: Path) -> None:
    """Ensures a directory exists."""
    path.mkdir(parents=True, exist_ok=True)

def safe_filename(text: str, max_len: int = 80) -> str:
    """Creates a safe filename from text."""
    if not text:
        return "unknown"
    # Keep alphanumeric, hyphen, underscore
    clean = re.sub(r'[^a-zA-Z0-9_.-]', '_', text)
    return clean[:max_len].strip('_')

def compute_sha256(file_path: Path) -> str:
    """Computes SHA256 hash of a file by streaming in chunks."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read in 64K chunks
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

async def write_stream_to_file(stream, file_path: Path, max_bytes: int) -> int:
    """Writes an async iterator stream to a file, enforcing max_bytes. Returns bytes written."""
    bytes_written = 0
    with open(file_path, "wb") as f:
        async for chunk in stream:
            bytes_written += len(chunk)
            if bytes_written > max_bytes:
                raise ValueError(f"File exceeds maximum allowed size of {max_bytes} bytes")
            f.write(chunk)
    return bytes_written


def safe_resolve_under(base_dir: Path, relative_path: str) -> Path:
    """Resolves a path securely inside a base directory, preventing traversal."""
    resolved_base = base_dir.resolve()
    target_path = (resolved_base / relative_path).resolve()
    
    if not str(target_path).startswith(str(resolved_base)):
        raise ValueError(f"Path traversal detected: {relative_path}")
        
    return target_path
