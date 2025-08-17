from abc import ABC, abstractmethod

class ScanningModule(ABC):
    """Abstract base class for all scanning modules."""

    @abstractmethod
    def scan(self, target: str, options: dict = None):
        """Run a scan on the given target."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the scanner."""
        pass
