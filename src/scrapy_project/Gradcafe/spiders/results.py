import scrapy
from ..items import GradcafeItem


class ResultsSpider(scrapy.Spider):
    name = "results"
    allowed_domains = ["thegradcafe.com"]
    start_urls = ["https://www.thegradcafe.com/survey/index.php?q=&t=a&o=&p=1"]

    def parse(self, response):
        rows = response.css("tr")

        for row in rows:
            tds = row.css("td")
            item = GradcafeItem()

            if len(tds) > 2:
                item["university"] = tds[0].css("div div::text").get(default=None).strip()
                item["program"] = (
                    tds[1].css("span:nth-of-type(1)::text").get(default=None).strip()
                )
                item["degree"] = (
                    tds[1].css("span:nth-of-type(2)::text").get(default=None).strip().upper()
                )
                item["date_posted"] = tds[2].css("::text").get(default=None).strip()
                item["decision_raw"] = tds[3].css("div::text").get(default=None).strip()
                item["season"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(2)::text""")
                    .get(default=None)
                    .strip()
                )
                item["status"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(3)::text""")
                    .get(default=None)
                    .strip()
                )
                item["score1_raw"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(4)::text""")
                    .get(default=None)
                    .strip()
                )
                item["score2_raw"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(5)::text""")
                    .get(default=None)
                    .strip()
                )
                item["score3_raw"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(6)::text""")
                    .get(default=None)
                    .strip()
                )
                item["score4_raw"] = (
                    row.css("""tr + tr td > div > div:nth-of-type(7)::text""")
                    .get(default=None)
                    .strip()
                )
                item["notes_raw"] = (
                    row.css("""tr + tr + tr td > p::text""").get(default=None).strip()
                )

                yield item

        next_page = response.css(
            "body > div.tw-mx-auto.tw-max-w-7xl.tw-px-4.sm\\:tw-px-6.lg\\:tw-px-8.md\\:tw-py-12.tw-py-8 "
            "> div.tw-flex.tw-flex-col.lg\\:tw-flex-row "
            "> div.tw-w-full.lg\\:tw-w-3\\/4.lg\\:tw-pr-8 "
            "> nav > div.tw--mt-px.tw-flex.tw-w-0.tw-flex-1.tw-justify-end "
            "> a::attr(href)"
        ).get()

        if next_page:
            yield response.follow(next_page, callback=self.parse)

        else:
            self.log("No more pages to scrape.")
