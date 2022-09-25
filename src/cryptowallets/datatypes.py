from dataclasses import dataclass


@dataclass(frozen=True)
class Wallet:
    """Wallet class with address and name."""
    address: str
    name: str

    def __repr__(self):
        return f"{self.name} {self.address}"
