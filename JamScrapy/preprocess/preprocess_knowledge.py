import scrapy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Knowledge


def process_knowledge():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    pages = engine.execute("select * from spider_jam_search where keyword='chatbot'")

    print(pages.rowcount)

    session = sessionmaker(bind=engine)()

    count = 0

    for p in pages:
        print(p.url, p.createtime)

        html = scrapy.Selector(text=p.body)
        lists = html.xpath('//ul[@class="search_result_list"]/li[@class="search_result"]').extract()

        if lists:
            for post in lists:
                post = scrapy.Selector(text=post)
                title = post.xpath('//div[@class="title"]/span/a[@class="search_result_link"]//text()').extract()
                abstract = post.xpath('//div[@class="snippet"]//text()').extract()
                score = post.xpath('//div[@class="title"]/span/a[@class="search_result_link"]/@search_score').extract()

                k = Knowledge()

                if title:
                    print('title:', ' '.join(title).strip())
                if abstract:
                    print('abstract:', ' '.join(abstract).replace('\\n', '').replace('...', '').strip())
                if score:
                    print('score:', float(score[0]))

                k.title = ' '.join(title).strip()
                k.abstract = ' '.join(abstract).replace('\\n', '').replace('...', '').strip()
                k.score = float(score[0])

                count += 1

                session.add(k)

    session.commit()
    session.close()

    return count


if __name__ == '__main__':
    count = process_knowledge()
    print(count)
    print("All Done")
