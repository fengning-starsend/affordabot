from typing import Protocol, Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class ExtractorClient(Protocol):
    """Protocol for extraction services that turn raw URLs into structured data."""

    async def extract(self, url: str, schema: Type[T]) -> T:
        """
        Extract structured data from a URL based on the provided Pydantic schema.

        Args:
            url: The URL to extract data from.
            schema: The Pydantic model class defining the desired structure.

        Returns:
            An instance of the schema populated with extracted data.
        """
        ...
