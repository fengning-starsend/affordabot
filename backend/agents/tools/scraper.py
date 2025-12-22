from llm_common.agents.tools import (
    BaseTool,
    ToolMetadata,
    ToolParameter,
    ToolResult,
)


class ScraperTool(BaseTool):
    """
    A tool for scraping web pages.
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="scraper",
            description="Scrapes a web page and returns the content.",
            parameters=[
                ToolParameter(
                    name="url",
                    type="string",
                    description="The URL of the web page to scrape.",
                    required=True,
                ),
            ],
        )

    async def execute(self, url: str) -> ToolResult:
        """
        Scrapes a web page and returns the content.

        Args:
            url: The URL of the web page to scrape.

        Returns:
            A ToolResult containing the scraped content.
        """
        # For now, this is a placeholder. A real implementation would go here.
        mock_content = f"Content of {url} would be scraped here."
        return ToolResult(success=True, data={"content": mock_content})
