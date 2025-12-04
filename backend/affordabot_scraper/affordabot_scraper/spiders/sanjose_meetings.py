import scrapy
from datetime import datetime

class SanJoseMeetingsSpider(scrapy.Spider):
    name = "sanjose_meetings"
    allowed_domains = ["sanjose.legistar.com"]
    start_urls = ["https://sanjose.legistar.com/Calendar.aspx"]

    def parse(self, response):
        # Skeleton implementation: Just prove we can fetch and parse
        rows = response.css("table.rgMasterTable tr.rgRow, table.rgMasterTable tr.rgAltRow")
        
        self.logger.info(f"Found {len(rows)} meeting rows")
        
        # For the skeleton, just yield a summary
        yield {
            "type": "meeting_list",
            "page_title": response.css("title::text").get(),
            "row_count": len(rows),
            "scraped_at": datetime.utcnow().isoformat(),
            "note": "Skeleton implementation - detailed parsing in Phase 1"
        }
