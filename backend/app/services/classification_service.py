from app.classification import get_classifier
from app.contracts import ClassificationResult
from app.repositories.block_repo import ExtractedBlockRepository
from app.repositories.classification_repo import ClassificationRepository
from app.repositories.document_repo import DocumentRepository


class ClassificationService:
    def __init__(
        self,
        blocks: ExtractedBlockRepository,
        documents: DocumentRepository,
        classifications: ClassificationRepository,
        classifier=None,
    ):
        self.blocks = blocks
        self.documents = documents
        self.classifications = classifications
        self.classifier = classifier or get_classifier()

    async def process(self, document_id: int) -> ClassificationResult:
        doc = await self.documents.get_by_id(document_id)
        rows = await self.blocks.list_for_document(document_id)
        text = "\n".join(b.text for b in rows)
        filename = doc.original_filename if doc else None
        result = self.classifier.classify(text, filename=filename)
        await self.classifications.save(document_id, result)
        await self.documents.set_classification(
            document_id, result.classified_type, result.document_family
        )
        from app.metrics import count_classification

        count_classification(result.classified_type)
        return result
