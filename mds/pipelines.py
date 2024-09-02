from urllib.parse import parse_qs, urlparse

import eyed3
import scrapy
from scrapy.pipelines.files import FilesPipeline


class StoryIdPipeline:
    def process_item(self, item: dict, spider: scrapy.Spider) -> dict:
        qs = parse_qs(urlparse(item["url"]).query)
        item["story_id"] = qs["user"][0] if qs.get("user") else None
        return item


class DownloadAudioPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        return request.url.split("/")[-1]


class ProcessAudioPipeline:
    def process_item(self, item: dict, spider: scrapy.Spider) -> dict:
        if getattr(spider, "utf8_tags", False):
            audio = eyed3.load(
                spider.settings["FILES_STORE"] / item["files"][0]["path"]
            )
            audio.tag.album = "Модель для сборки"
            audio.tag.artist = self.convert_encoding(audio.tag.artist)
            audio.tag.title = self.convert_encoding(audio.tag.title)
            audio.tag.save(encoding="utf-8")
        return item

    @staticmethod
    def convert_encoding(
        text: str, source: str = "latin-1", destination: str = "cp1251"
    ) -> str:
        try:
            return text.encode(source).decode(destination)
        except ValueError:
            return text
