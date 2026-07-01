"""Section-aware chunking: group consecutive clauses by section, flushing when
the section changes or a size bound is hit. Page/section metadata is preserved
for citation-grounded retrieval."""
from app.contracts import Chunk

_MAX_CHARS = 900


def chunk_clauses(
    clauses: list[tuple[int | None, str | None, str]], max_chars: int = _MAX_CHARS
) -> list[Chunk]:
    """clauses: ordered (page_number, section_name, text)."""
    chunks: list[Chunk] = []
    buf: list[tuple[int | None, str | None, str]] = []
    idx = 0

    def flush() -> None:
        nonlocal idx, buf
        if buf:
            chunks.append(
                Chunk(
                    chunk_index=idx,
                    page_number=buf[0][0],
                    section_name=buf[0][1],
                    text=" ".join(t for _, _, t in buf),
                )
            )
            idx += 1
            buf = []

    for page, section, text in clauses:
        if buf:
            same_section = section == buf[-1][1]
            size = sum(len(t) for _, _, t in buf) + len(text)
            if not same_section or size > max_chars:
                flush()
        buf.append((page, section, text))
    flush()
    return chunks
