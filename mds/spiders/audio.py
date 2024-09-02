import pathlib
import typing as t

import scrapy
from scrapy import http


def get_bool(value: str) -> bool:
    try:
        return bool(int(value))
    except ValueError:
        if value in ("True", "true"):
            return True
        if value in ("False", "false"):
            return False
        raise ValueError(
            "Supported values for boolean settings "
            "are 0/1, True/False, '0'/'1', "
            "'True'/'False' and 'true'/'false'"
        )


class Spider(scrapy.Spider):
    name = "audio"
    custom_settings = {
        "DOWNLOAD_TIMEOUT": 60.0,
        "FILES_STORE": pathlib.Path(__file__).resolve().parent.parent.parent / "audio",
        "ITEM_PIPELINES": {
            "mds.pipelines.DownloadAudioPipeline": 100,
            "mds.pipelines.ProcessAudioPipeline": 100,
        },
    }

    utf8_tags: bool = False

    links: list[str] = [
        "http://mds.kallisto.ru/grey2000/2021/11/01_Alan_Kubatiev_-_Strudel_po-venski.mp3",
    ]

    def __init__(self, *args, **kwargs):
        if links := kwargs.pop("links", None):
            kwargs["links"] = links.split(",")
        if utf8_tags := kwargs.pop("utf8_tags", None):
            kwargs["utf8_tags"] = get_bool(utf8_tags)
        super().__init__(*args, **kwargs)

    def start_requests(self) -> t.Generator:
        yield http.Request("http://www.mds-club.ru/cgi-bin/index.cgi")

    def parse(self, _: http.HtmlResponse) -> t.Generator:
        for url in self.links:
            yield {"file_urls": [url]}
