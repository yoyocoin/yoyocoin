"""
Hardcoded data for the blockchain (use for genesis validation)
"""
from .block import Block

__all__ = ["GENESIS_BLOCK", "developer_address"]

developer_address = "A5tr0VkOLYQNqP0RK9mfzOFnF0B8iSH7XRc6/SRIVixL"

GENESIS_BLOCK = Block(
    index=0,
    previous_hash="0",
    forger=developer_address,
    timestamp=0,
    signature="Fh39IpZ3jBIHyg+nAowsEGp69GS9UgdQXFyKoXLwItptdzMroZJBmxdxKlOdPiLY1LkI3Ogr35S1iC4GLDWGLQ==",
)
