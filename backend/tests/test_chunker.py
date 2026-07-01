from app.rag import chunk_clauses


def test_groups_consecutive_clauses_by_section():
    clauses = [
        (1, "FEES", "Processing fee applies."),
        (1, "FEES", "Late fee applies."),
        (2, "RENEWAL", "Auto renews monthly."),
    ]
    chunks = chunk_clauses(clauses)
    assert len(chunks) == 2
    assert chunks[0].section_name == "FEES" and chunks[0].page_number == 1
    assert "Processing fee" in chunks[0].text and "Late fee" in chunks[0].text
    assert chunks[1].section_name == "RENEWAL"
    assert [c.chunk_index for c in chunks] == [0, 1]


def test_size_bound_splits_a_long_section():
    big = "x" * 600
    clauses = [(1, "S", big), (1, "S", big), (1, "S", big)]
    chunks = chunk_clauses(clauses, max_chars=900)
    assert len(chunks) >= 2  # 1800 chars of same section must split


def test_empty():
    assert chunk_clauses([]) == []
