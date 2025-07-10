# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime
import json
import os


class JsonWriterPipeline:
    def __init__(self, raw_data_dir):
        self.raw_data_dir = raw_data_dir
        os.makedirs(self.raw_data_dir, exist_ok=True)
        self.filename = os.path.join(
            self.raw_data_dir,
            f"gradcafe_raw_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl",
        )

    @classmethod
    def from_crawler(cls, crawler):
        raw_data_dir = crawler.settings.get("RAW_DATA_DIR")
        if not raw_data_dir:
            crawler.logger.error("RAW_DATA_DIR setting is not defined in settings.py")
            raise ValueError("RAW_DATA_DIR setting required.")
        return cls(raw_data_dir)

    def open_spider(self, spider):
        spider.logger.info(f"Opened JSONL file for writing: {self.filename}")

    def close_spider(self, spider):
        spider.logger.info(f"closed JSONL file: {self.filename}")

    def process_item(self, item, spider):
        if item.get("program") and item.get("university") and item.get("decision_raw"):
            try:
                with open(self.filename, "a", encoding="utf-8") as f:
                    json.dump(dict(item), f, ensure_ascii=False)
                    f.write("\n")
            except (OSError, TypeError) as e:
                spider.logger.error(f"failed to write to file : {e}")
        return item
