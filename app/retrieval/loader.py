from pathlib import Path


SUPPORTED_KB_SUFFIXES = {".md", ".txt"}


def load_markdown_documents(directory: str | Path) -> list[tuple[str, str]]:
    """
    Load markdown/text files from a directory recursively.

    Returns:
        A list of tuples in the form (filename, text_content).
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {directory}")

    documents: list[tuple[str, str]] = []

    for path in sorted(directory.rglob("*")):
        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_KB_SUFFIXES:
            continue

        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append((path.name, text))

    return documents