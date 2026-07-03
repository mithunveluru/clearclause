from app.analysis.analyzers.consumer import ConsumerAnalyzer
from app.analysis.analyzers.credit_card import CreditCardAnalyzer
from app.analysis.analyzers.patta import PattaAnalyzer
from app.analysis.analyzers.rental import RentalAnalyzer
from app.analysis.analyzers.sale_deed import SaleDeedAnalyzer
from app.analysis.base import BaseAnalyzer
from app.core.constants import ClassifiedType
from app.entities.extractors.loan import LoanEntityExtractor
from app.entities.extractors.subscription import SubscriptionEntityExtractor

# classified_type -> analyzer; unregistered types fall back to V1 detection
_ANALYZERS: dict[str, BaseAnalyzer] = {
    ClassifiedType.LOAN: ConsumerAnalyzer(ClassifiedType.LOAN, LoanEntityExtractor()),
    ClassifiedType.SUBSCRIPTION: ConsumerAnalyzer(
        ClassifiedType.SUBSCRIPTION, SubscriptionEntityExtractor()
    ),
    ClassifiedType.CREDIT_CARD: CreditCardAnalyzer(),
    ClassifiedType.RENTAL_CONTRACT: RentalAnalyzer(),
    ClassifiedType.PATTA: PattaAnalyzer(),
    ClassifiedType.SALE_DEED: SaleDeedAnalyzer(),
}


def get_analyzer(classified_type: str | None) -> BaseAnalyzer | None:
    return _ANALYZERS.get(classified_type or "")
