"""Measure OCR accuracy against hand-checked ground truth.

Without this, no OCR change can be justified — including leaving it alone. The
existing tests prove text comes back, not that it is the right text.

Corpus layout (gitignored; these are real documents, never commit them):
    tests/fixtures/ocr_corpus/<name>.pdf   the scan
    tests/fixtures/ocr_corpus/<name>.txt   what it actually says

Run inside the backend container (needs tesseract + poppler):
    docker compose exec backend python -m scripts.ocr_accuracy

Reports word error rate, not the character error rate OCR papers quote. Words are
the unit that decides whether this product works: the detection rules and entity
extractors match on words, so "2 percent" read as "Z percent" is one failure
either way, and WER is what predicts the pipeline's own accuracy. It is also
O(words^2) instead of O(chars^2), which keeps it stdlib-only and fast.
"""
import re
import sys
import time
from pathlib import Path

from app.ocr import get_ocr_provider

CORPUS = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "ocr_corpus"
SCAN_SUFFIXES = (".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff")


def words(text: str) -> list[str]:
    """Alphanumeric runs, lowercased. Punctuation and case are not OCR's job."""
    return re.findall(r"[^\W_]+", text.lower())


def distance(reference: list[str], hypothesis: list[str]) -> int:
    """Levenshtein over token lists, two rows at a time."""
    previous = list(range(len(hypothesis) + 1))
    for i, want in enumerate(reference, start=1):
        current = [i]
        for j, got in enumerate(hypothesis, start=1):
            current.append(
                min(
                    previous[j] + 1,                    # word dropped
                    current[j - 1] + 1,                 # word invented
                    previous[j - 1] + (want != got),    # word misread
                )
            )
        previous = current
    return previous[-1]


def wer(reference: str, hypothesis: str) -> float:
    want = words(reference)
    return distance(want, words(hypothesis)) / len(want) if want else 0.0


def _self_check() -> None:
    assert wer("a b c", "a b c") == 0.0
    assert wer("a b c d", "a x c d") == 0.25          # misread
    assert wer("a b c d", "a b c") == 0.25            # dropped
    assert wer("a b c", "a b z c") == 1 / 3           # invented
    assert wer("2 percent", "Z percent!") == 0.5      # case and punctuation ignored


def scan_for(truth: Path) -> Path | None:
    for suffix in SCAN_SUFFIXES:
        candidate = truth.with_suffix(suffix)
        if candidate.exists():
            return candidate
    return None


def main() -> int:
    truths = sorted(CORPUS.glob("*.txt")) if CORPUS.is_dir() else []
    if not truths:
        _self_check()
        print(f"self-check passed. No corpus yet — add <name>{SCAN_SUFFIXES[0]} + <name>.txt "
              f"pairs to {CORPUS}")
        return 0

    provider = get_ocr_provider()
    total_words = total_errors = 0

    for truth in truths:
        scan = scan_for(truth)
        if scan is None:
            print(f"{truth.stem:<28} SKIP  no scan beside {truth.name}")
            continue

        started = time.monotonic()
        text = " ".join(b["text"] for b in provider.extract(str(scan)))
        elapsed = time.monotonic() - started

        want = words(truth.read_text())
        if not want:
            print(f"{truth.stem:<28} SKIP  {truth.name} is empty")
            continue
        errors = distance(want, words(text))
        total_words += len(want)
        total_errors += errors
        print(f"{truth.stem:<28} WER {errors / len(want):6.1%}  {len(want):5d} words  {elapsed:5.1f}s")

    if total_words:
        print(f"{'OVERALL':<28} WER {total_errors / total_words:6.1%}  {total_words:5d} words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
