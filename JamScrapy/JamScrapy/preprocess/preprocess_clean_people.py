from tqdm import tqdm
from sqlalchemy import create_engine, text
from JamScrapy import config
import string
import scrapy

PROFILES = dict()


def initial_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"select profileurl, username from people_profile")

    for r in results:
        url = r.profileurl.split('/')[-1]
        PROFILES[url] = r.username.strip()

    print('PROFILES DICT:', len(PROFILES))


def get_people_username(profileurl):
    url = profileurl.split('/')[-1]

    if len(PROFILES) > 0 and url in PROFILES.keys():
        return PROFILES[url]
    else:
        return ''


def fill_username_people():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(
        f"select id,displayname,profileurl from jam_people_from_post where (username ='' or username is null) and displayname <> 'Alumni'").fetchall()

    print('people_from_post:', len(results))

    set_people_no_profile = set()
    for r in tqdm(results):
        username = get_people_username(r.profileurl)

        if username != '':
            engine.execute(f"update jam_people_from_post set username = '{username}' where id = {r.id}")
        else:
            set_people_no_profile.add(r.profileurl)

    print('people_no_profile (people_from_post):', len(set_people_no_profile))


def fill_username_post():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(
        f"select username, posturl from jam_people_from_post where username is not null and username <> '' and roletype='creator'").fetchall()

    print('post:', len(results))

    DICT_PEOPLE = dict()
    for item in results:
        url = item.posturl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
        DICT_PEOPLE[url] = item.username.strip()

    results = engine.execute(
        f"select id, url, author from jam_post where (username is null or username = '') and author <> 'Alumni'").fetchall()

    print(len(results))

    set_people_no_profile = set()
    for p in tqdm(results):
        url = p.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
        if url in DICT_PEOPLE.keys():
            engine.execute(f"update jam_post set username = '{DICT_PEOPLE[url]}' where id = {p.id}")
        else:
            set_people_no_profile.add(url)

    print('people_no_profile (post):', len(set_people_no_profile))


def isAllZh(s):
    '''if there is Chines return True'''

    for c in s:
        if '\u4e00' <= c <= '\u9fa5':
            return True
    return False


def get_name_from_email(email):
    name = email.split('@')[0]
    name = name.rstrip(string.digits)
    name = "".join(name)
    name = string.capwords(name, sep='.')
    email_name = name.replace('.', ' ')
    return email_name


def process_displayname(people):
    displayname = people.displayname.replace('\\', '').strip('.').strip(' ').strip('@')
    displayname = string.capwords(displayname, sep=' ')
    displayname_without_dot = displayname.replace('.', ' ')

    result = people.displayname

    if people.email:
        email_name = get_name_from_email(people.email)
        '''there is email, and email_name == displayname, update displaynameformatted = displayname'''

        if email_name != displayname_without_dot:
            displayname_without_dot = displayname_without_dot.replace('-', '').replace("'", '')
            for item in displayname_without_dot.split(" "):
                if not item.isalpha() or isAllZh(item):
                    result = email_name
                    break

            if len(displayname_without_dot.split(" ")[0]) == 1:
                result = email_name
    else:
        displayname_without_dot = displayname_without_dot.replace('-', '').replace("'", '')

        for item in displayname_without_dot.split(' '):
            if not item.isalpha() or isAllZh(item):
                return None

    # make displaynameformatted like O'ben change to O'Ben
    if result is not None:
        if "'" in result:
            array = result.split("'")
            part_of_name = array[1].capitalize()

            result = array[0] + "'" + part_of_name

    return result


def clean_dirty_displayname(update_all_flag=False):
    '''
        :param update_all: True: displaynameformatted whatever ; False: displaynameformatted is null or '' ;
        :return:
    get info from dataBase
    '''
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    if not update_all_flag:
        sql = "select id, displayname, email, displaynameformatted from people_profile where displaynameformatted is null"
    else:
        sql = "select id, displayname, email, displaynameformatted from people_profile"

    peoples = engine.execute(sql).fetchall()

    print('portal profile:', update_all_flag, len(peoples))

    if len(peoples) == 0:
        return

    list_update_people = []
    list_can_not_update_people = []

    for people in tqdm(peoples):
        displaynameformatted = process_displayname(people)

        if displaynameformatted is not None:
            list_update_people.append({"id": people.id, "name": displaynameformatted})

            sql = "update people_profile set displaynameformatted = :name where id = :id"
            # sql = '''update people_profile set displaynameformatted = "%s" Where id="%s";''' % (p.displayname[3], d[0])
            engine.execute(text(sql), {"id": people.id, "name": displaynameformatted})
        else:
            list_can_not_update_people.append(people)
            print(people)

    '''
    if displayname can be formatted:
        save in update_data.csv 
    else:
        save in can_not_update.csv
    '''
    # cate = ['id', 'displayname', 'email', 'displaynameformatted']
    # df_update = DataFrame(update_people, columns=cate)
    # df_not_update = DataFrame(can_not_update_people, columns=cate)
    # df_update.to_csv('update_data.csv')
    # df_not_update.to_csv('can_not_update.csv')

    return len(list_update_people)


def fill_people_profile_gender():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    sql = '''select p.id, p.username, p.gender, s.body from people_profile p inner join spider_portal_profile s
               on p.username = s.username where p.gender is null and s.body <> '[]' order by p.id'''
    peoples = engine.execute(sql).fetchall()

    print('portal without gender:', len(peoples))

    count_update_gender = 0
    for p in tqdm(peoples):
        html = scrapy.Selector(text=p.body)
        display_name = html.xpath('//header[@class="full_name"]/text()').extract()

        if display_name:
            gender = display_name[1].split(' ')[0].replace('\\n', '').strip()

        gender_flag = None
        if gender == 'Mr.':
            gender_flag = 1
        elif gender == 'Ms.':
            gender_flag = 0

        if gender_flag is not None:
            sql = "update people_profile set gender = :g where id = :id"
            engine.execute(text(sql), {"id": p.id, "g": gender_flag})

            count_update_gender += 1

    print('---------------------------------------------------')
    print('portal gender updated:', count_update_gender, '/', len(peoples))


if __name__ == '__main__':
    initial_profiles()

    fill_people_profile_gender()

    count = clean_dirty_displayname(update_all_flag=False)
    print('displayname formatted:', count)
    print('--------------------------------------------------')
    print('fill_username_people')
    fill_username_people()
    print('--------------------------------------------------')
    print('fill_username_post')
    fill_username_post()

    print("All Done")
