import asyncio

from crawl4ai import AsyncWebCrawler, BrowserConfig

browser_conf = BrowserConfig(
    browser_type="chrome",
    headless=True,
    text_mode=True,
)

async def scrape_website(url):
    """Asynchronously scrape a website and return the content as markdown."""
    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url=url,
        )
        # print(result.markdown)
        # store the result in experiment/crawl_step_1_output.txt
        # with open(output_file, "w") as f:
        #     f.write(result.markdown)
        return result.markdown

if __name__ == "__main__":
    asyncio.run(scrape_website("https://www.rang-und-namen.de/"))