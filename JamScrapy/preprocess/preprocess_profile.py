import scrapy
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Profile


def process_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    session = sessionmaker(bind=engine)()
    profiles = engine.execute('SELECT * FROM jam_profile_spider ORDER BY peoplename')

    print(profiles.rowcount)

    for p in profiles:
        print(p.id, p.peoplename, p.url, p.createtime)

        html = scrapy.Selector(text=p.body)
        user_name = html.xpath('//div[@class="viewJobInfo"]/text()').extract()
        display_name = html.xpath('//span[@class="member_name"]/text()').extract()
        mobile = html.xpath('//div[@class="member_more_info"]/table/tbody/tr/td[label="Mobile: "]/text()').extract()
        email = html.xpath(
            '//div[@class="member_more_info"]/table/tbody/tr/td[label="Primary Email: "]/a/text()').extract()
        avatar = html.xpath('//div[@class="avatar-greybox"]/img/@src').extract()
        managers = html.xpath('''//div[@class="clearfix org-chart-sections" and @aria-label="Managers"]
            //div[@class="badgeDetails"]/ul/li/a/text()''').extract()
        manager_profiles = html.xpath('''//div[@class="clearfix org-chart-sections" and @aria-label="Managers"]
            //div[@class="badgeDetails"]/ul/li/a/@href''').extract()
        reports = html.xpath('''//div[@class="clearfix org-chart-sections" and @aria-label="Direct Reports"]
            //div[@class="badgeDetails"]/ul/li/a/text()''').extract()
        report_profiles = html.xpath('''//div[@class="clearfix org-chart-sections" and @aria-label="Direct Reports"] 
            //div[@class="badgeDetails"]/ul/li/a/@href''').extract()

        if user_name and display_name:
            profile = Profile(profileurl=p.url, username=user_name[0], displayname=display_name[0])

            if avatar:
                profile.avatar = avatar[0]

            if managers and manager_profiles and len(managers) == len(manager_profiles):
                json_managers = []
                for i in range(len(managers)):
                    json_managers.append({'name': managers[i], 'url': manager_profiles[i]})
                profile.managers = json.dumps(json_managers)

            if reports and report_profiles and len(reports) == len(report_profiles):
                json_reports = []
                for i in range(len(reports)):
                    json_reports.append({'name': reports[i], 'url': report_profiles[i]})
                profile.reports = json.dumps(json_reports)

            print(profile.reports)
            session.add(profile)

    session.commit()


if __name__ == '__main__':
    # process_profiles()
    print("All Done")
