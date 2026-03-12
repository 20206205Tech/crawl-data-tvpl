from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from crawler.spiders.document_detail_spider import DocumentDetailSpider


def main():
    settings = get_project_settings()
    settings.set('FEEDS', {
        '../data/document_detail.jsonl': {'format': 'jsonl', 'overwrite': True}
    })

    process = CrawlerProcess(settings)
    process.crawl(DocumentDetailSpider)
    process.start()


if __name__ == "__main__":
    main()