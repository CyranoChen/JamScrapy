import scrapy
import json

from tqdm import tqdm

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import Profile


def process_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    profiles = engine.execute(f"SELECT * FROM spider_jam_profile where id >= {config.LATEST_JAM_PROFILE_SPIDER_ID} "
                              f"and username is not null ORDER BY peoplename ").fetchall()

    print(len(profiles))

    session = sessionmaker(bind=engine)()

    count = 0

    for p in tqdm(profiles):
        #print(p.id, p.username, p.peoplename, p.url, p.createtime)

        profile = session.query(Profile).filter(Profile.username == p.username).first()
        #print(p.username, p.peoplename, p.url, p.id)

        if profile:
            count += 1

        html = scrapy.Selector(text=p.body)
        # user_name = html.xpath('//div[@class="viewJobInfo"]/text()').extract()
        # display_name = html.xpath('//span[@class="member_name"]/text()').extract()
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

        print(mobile, email, avatar, managers, reports)

        if profile is None:
            profile = Profile(profileurl=p.url.strip(), username=p.username.strip(), displayname=p.peoplename.strip())

        if avatar:
            profile.avatar = avatar[0]

        if mobile:
            profile.mobile = mobile[0]

        if email:
            profile.email = email[0]

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

        if profile:
            session.merge(profile)

    session.commit()
    session.close()

    return count


if __name__ == '__main__':
    count = process_profiles()

    print('Duplicate:', count)
    print("All Done")
