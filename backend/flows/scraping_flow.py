import os
import subprocess
from prefect import flow, task, get_run_logger
from supabase import create_client, Client

@task
def fetch_active_sources():
    logger = get_run_logger()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    
    supabase: Client = create_client(url, key)
    response = supabase.table("sources").select("*").eq("status", "active").execute()
    logger.info(f"Found {len(response.data)} active sources")
    return response.data

@task
def run_spider(source):
    logger = get_run_logger()
    source_id = source["id"]
    handler = source.get("handler")
    source_method = source.get("source_method", "scrape")

    if not handler:
        logger.error(f"No handler specified for source {source_id}")
        return
    
    if source_method != "scrape":
        logger.warning(f"Source {source_id} has method '{source_method}', skipping spider execution")
        return

    logger.info(f"Starting spider {handler} for source {source_id}")
    
    # Run scrapy as a subprocess
    # We assume we are in the project root, so we need to point to backend/affordabot_scraper
    cwd = os.path.join(os.getcwd(), "backend", "affordabot_scraper")
    scrapy_bin = os.path.join(os.getcwd(), "backend", "venv", "bin", "scrapy")
    
    try:
        result = subprocess.run(
            [scrapy_bin, "crawl", handler, "-a", f"source_id={source_id}"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"Spider finished successfully: {result.stdout}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Spider failed: {e.stderr}")
        raise

@flow(name="Scrape All Sources")
def scrape_all_flow():
    sources = fetch_active_sources()
    for source in sources:
        run_spider.submit(source)

if __name__ == "__main__":
    scrape_all_flow()
