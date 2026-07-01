import asyncio

from app.ai.prompts import QA_SYSTEM
from app.contracts import Chunk
from app.services.qa_service import QAService


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
    # the model saw the QA grounding system prompt and the excerpts (not outside knowledge)
    assert client.seen["system"] == QA_SYSTEM
    assert "two months rent" in client.seen["prompt"]
    assert "Rs 25000" in client.seen["prompt"]
