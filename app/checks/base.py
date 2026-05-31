##This defines what every security check must look like.

from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CheckResult:
    check_id: str
    resource_id: str
    passed: bool
    severity: str
    description: str

class BaseCheck(ABC):
    check_id: str
    severity: str

    @abstractmethod
    def run(self, client) -> list[CheckResult]:
        ...
