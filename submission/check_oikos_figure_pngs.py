from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "figures"

def main() -> None:
    for i in range(1, 6):
        path = OUT / f"Figure_{i}.png"
        if not path.is_file():
            raise SystemExit(f"missing: {path}")
        raw = path.read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
            raise SystemExit(f"not PNG: {path}")
        if len(raw) < 10000:
            raise SystemExit(f"suspiciously small figure: {path} ({len(raw)} bytes)")
        print(f"{path.name}: {len(raw)} bytes")

if __name__ == "__main__":
    main()
