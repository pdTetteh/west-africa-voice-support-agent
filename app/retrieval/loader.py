from pathlib import Path


def load_markdown_documents(directory: str | Path) -> list[tuple[str, str]]:
    """
    Load markdown files from a directory.

    Returns:
        A list of tuples in the form (filename, text_content).
    """
    directory = Path(directory)

    if not directory.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {directory}")

    documents: list[tuple[str, str]] = []

    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            documents.append((path.name, text))

    return documents