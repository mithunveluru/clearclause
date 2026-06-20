class DocStatus:
    """Document processing states (full flow wired in Phase 10)."""

    UPLOADED = "uploaded"
    OCR_PROCESSING = "ocr_processing"
    OCR_DONE = "ocr_done"
    ANALYSIS_PROCESSING = "analysis_processing"
    ANALYSIS_DONE = "analysis_done"
    REPORT_READY = "report_ready"
    FAILED = "failed"


class JobStatus:
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
