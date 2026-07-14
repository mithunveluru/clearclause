import asyncio

from app.ai.prompts import QA_SYSTEM
from app.contracts import Chunk
from app.services.qa_service import QAService, best_snippet


class FakeClient:
    model = "fake"

    def __init__(self):
        self.calls: list[dict] = []

    def generate(self, prompt, system=""):
        self.calls.append({"prompt": prompt, "system": system})
        return "The deposit is two months' rent."

    @property
    def seen(self) -> dict:
        # first call is always the QA answer call
        return self.calls[0] if self.calls else {}


class FakeRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def search(self, document_id, query, top_k=5):
        return self.chunks

    def search_knowledge(self, query, family=None, top_k=3):
        return []


def test_qa_refuses_when_no_chunks_retrieved():
    svc = QAService(retriever=FakeRetriever([]), client=FakeClient())
    ans = asyncio.run(svc.answer(1, "Can rent be increased?"))
    assert ans.citations == []
    assert "couldn't find" in ans.answer.lower()
    assert "no relevant" in ans.confidence_note.lower()


def test_qa_grounds_answer_and_cites_sources():
    chunks = [
        Chunk(chunk_index=0, page_number=2, section_name="Deposit", text="The security deposit is two months rent."),
        Chunk(chunk_index=1, page_number=3, section_name="Rent", text="Rent is Rs 25000 per month."),
    ]
    client = FakeClient()
    svc = QAService(retriever=FakeRetriever(chunks), client=client)
    ans = asyncio.run(svc.answer(1, "How much is the deposit?"))

    # answered, cited with page/section, grounded note
    assert ans.answer
    assert ans.citations and ans.citations[0].page == 2 and ans.citations[0].section == "Deposit"
    assert "only" in ans.confidence_note.lower()
    # The model saw only the prompt and excerpts
    assert client.seen["system"] == QA_SYSTEM
    assert "two months rent" in client.seen["prompt"]
    assert "Rs 25000" in client.seen["prompt"]


def test_citation_snippet_supports_the_claim():
    # A chunk is a whole section; cite precisely
    chunk = (
        "A processing fee of 2.5 percent of the sanctioned amount is payable upon disbursal. "
        "The borrower shall pay a prepayment penalty of 4 percent on any amount foreclosed "
        "within the first 12 months. "
        "A late payment charge of 3 percent per month applies on overdue EMIs."
    )
    snippet = best_snippet(
        chunk,
        "What is the prepayment penalty?",
        "The prepayment penalty is 4 percent on amounts foreclosed within 12 months.",
    )

    assert "prepayment penalty of 4 percent" in snippet
    assert "processing fee" not in snippet


def test_citation_snippet_tracks_the_question_asked():
    chunk = (
        "A processing fee of 2.5 percent is payable upon disbursal. "
        "A late payment charge of 3 percent per month applies on overdue EMIs."
    )
    assert "late payment charge" in best_snippet(chunk, "What happens if I pay late?", "")
    assert "processing fee" in best_snippet(chunk, "What is the processing fee?", "")


def test_citation_snippet_falls_back_when_nothing_matches():
    chunk = "The agreement is governed by the laws of India."
    assert best_snippet(chunk, "zzz qqq", "") == chunk
