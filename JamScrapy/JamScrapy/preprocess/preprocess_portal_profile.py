import scrapy
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from JamScrapy import config
from JamScrapy.preprocess.entity import PortalProfile


def process_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    profiles = engine.execute('SELECT * FROM spider_portal_profile where body <> "[]" and id >= 99486 ORDER BY username')

    print(profiles.rowcount)

    session = sessionmaker(bind=engine)()

    count = 0

    for p in profiles:
        print(p.id, p.username, p.url, p.createtime)

        profile = session.query(PortalProfile).filter(PortalProfile.username == p.username).first()
        print(p.username, profile)

        if profile:
            count += 1

        html = scrapy.Selector(text=p.body)
        user_name = html.xpath('//li[@class="uid"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        display_name = html.xpath('//div[@class="profile-header"]//header[@class="full_name"]/text()').extract()
        board_area = html.xpath(
            '//li[@class="organisation_board_area"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        functional_area = html.xpath(
            '//li[@class="functional_area"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        cost_center = html.xpath(
            '//li[@class="cost_center"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        office_location = html.xpath(
            '//li[@class="office_location"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        manager = html.xpath(
            '//li[@class="manager_link"]//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        local_time = html.xpath(
            '//li[@class="local_time"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        email = html.xpath(
            '//li[@class="email_link"]//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        phone = html.xpath(
            '//li[@class="work_phone"]//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        mobile = html.xpath(
            '//li[@class="mobile_phone"]//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()
        address = html.xpath(
            '//li[@class="office_address"]//div[@class="table-cell"]/span[@class="value"]/text()').extract()
        assistant = html.xpath(
            '//li[@class="assistant_link"]//div[@class="table-cell"]/span[@class="value"]/a/text()').extract()

        if profile is None and user_name and display_name:
            profile = PortalProfile(profileurl=p.url,
                                    username=user_name[0].replace('\\n', '').strip(),
                                    displayname=display_name[0].replace('\\n', '').strip(),
                                    # boardarea = board_area[0],
                                    # functional_area = functional_area[0],
                                    # costcenter=cost_center[0].replace('\\n', '').replace('\\xa0\\xa0', ''),
                                    # officelocation = office_location[0],
                                    # manager = manager[0],
                                    # localtime = local_time[0],
                                    email=email[0].replace('\\n', ''),
                                    # phone = phone[0],
                                    # mobile = mobile[0],
                                    # address = address[0]
                                    )

            if board_area:
                profile.boardarea = board_area[0].replace('\\n', '').strip()

            if functional_area:
                profile.functionalarea = functional_area[0].replace('\\n', '').strip()

            if cost_center:
                profile.costcenter = cost_center[0].replace('\\n', '').replace('\\xa0\\xa0', '').strip()

            if office_location:
                profile.officelocation = office_location[0].replace('\\n', '').replace('\\xa0\\xa0', '').strip()

            if manager:
                profile.manager = manager[0].replace('\\n', '').strip()

            if local_time:
                profile.localinfo = local_time[0].replace('\\n', '').strip()

            if phone:
                profile.phone = phone[0].replace('\\n', '').strip()

            if mobile:
                profile.mobile = mobile[0].replace('\\n', '').strip()

            if address:
                profile.address = address[0].replace('\\n', '').strip()

            if assistant:
                profile.assistant = assistant[0].replace('\\n', '').strip()

            if profile:
                session.merge(profile)

    session.commit()
    session.close()

    return count


def fill_displayname_portal_profile():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    engine.execute("update portal_profile set displayname = (select displayname from jam_profile "
                   "where jam_profile.username = portal_profile.username) "
                   "where portal_profile.displayname is null or portal_profile.displayname = ''")


if __name__ == '__main__':
    count = process_profiles()
    print('Duplicate:', count)

    fill_displayname_portal_profile()


    print("All Done")
