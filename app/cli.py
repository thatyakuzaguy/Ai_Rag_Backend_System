import argparse
from pathlib import Path

from app.core.dependencies import get_rag_service


def ingest_path(path: Path) -> int:
    rag = get_rag_service()
    files = [path] if path.is_file() else list(path.rglob("*"))
    total = 0
    for file_path in files:
        if file_path.suffix.lower() not in {".txt", ".md", ".csv"}:
            continue
        text = file_path.read_text(encoding="utf-8", errors="replace")
        total += rag.ingest_text(text=text, source=str(file_path), metadata={"path": str(file_path)})
    return total


def main() -> None:
    parser = argparse.ArgumentParser(description="AI RAG backend utilities")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest a file or folder")
    ingest.add_argument("path", type=Path)

    args = parser.parse_args()
    if args.command == "ingest":
        chunks = ingest_path(args.path)
        print(f"Indexed {chunks} chunks")


if __name__ == "__main__":
    main()
