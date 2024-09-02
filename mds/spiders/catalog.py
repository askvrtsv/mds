import datetime as dt
import typing as t

import scrapy
from scrapy import http


class Spider(scrapy.Spider):
    name = "catalog"
    custom_settings = {
        "ITEM_PIPELINES": {
            "mds.pipelines.StoryIdPipeline": 300,
        },
    }

    def start_requests(self) -> t.Iterable[http.Request]:
        yield http.Request(
            "http://www.mds-club.ru/cgi-bin/index.cgi?r=84&lang=rus",
            callback=self.parse_listing,
        )

    def parse_listing(self, response: http.HtmlResponse) -> t.Generator:
        # Пагинация
        next_url = response.xpath(
            '//div[@id="roller_active"]/following-sibling::div/a/@href'
        ).get()
        if next_url:
            yield http.Request(next_url, callback=self.parse_listing)

        # Рассказы
        for i, story in enumerate(response.css("#catalogtable tbody tr"), 1):
            if not (story_url := story.xpath("./td[1]/a/@href").get()):
                self.logger.warn("Story at %s (row: %s) has no link", response.url, i)
                continue

            yield http.Request(
                story_url,
                callback=self.parse_story_file,
                cb_kwargs={
                    "story": {
                        "author": story.xpath("./td[2]/a/text()").get(),
                        "title": story.xpath("./td[3]/a/text()").get(),
                        "date": self._extract_story_date(story),
                        "station": story.xpath("./td[6]/a/text()").get(),
                        "url": story_url,
                    },
                },
            )

    def parse_story_file(self, response: http.HtmlResponse, story: dict) -> t.Generator:
        yield {
            **story,
            "mp3_url": response.xpath(
                '//td/a[starts-with(@href, "http://mds.kallisto.ru/")]/@href'
            ).get(),
        }

    @staticmethod
    def _extract_story_date(story: scrapy.Selector) -> str | None:
        if not (story_date := story.xpath("./td[4]/a/text()").get()):
            return None
        try:
            return dt.datetime.strptime(story_date, "%d.%m.%Y").date().isoformat()
        except Exception as _:
            return None
