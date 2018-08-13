from tqdm import tqdm
from sqlalchemy import create_engine
from JamScrapy import config

PROFILES = dict()


def initial_profiles():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    results = engine.execute(f"select profileurl, username from people_profile")

    for r in results:
        url = r.profileurl.split('/')[-1]
        PROFILES[url] = r.username.strip()


def get_people_username(profileurl):
    url = profileurl.split('/')[-1]

    if len(PROFILES) > 0 and url in PROFILES.keys():
        return PROFILES[url]
    else:
        return ''


def fill_username_people():
    initial_profiles()

    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(
        f"select id,displayname,profileurl from jam_people_from_post where (username ='' or username is null) and displayname <> 'Alumni'")

    print(results.rowcount)

    for r in tqdm(results):
        username = get_people_username(r.profileurl)

        if username != '':
            engine.execute(f"update jam_people_from_post set username = '{username}' where id = {r.id}")
        else:
            print('not found', r.profileurl)


def fill_username_post():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    results = engine.execute(f"select username, posturl from jam_people_from_post where username is not null and username <> '' and roletype='creator'").fetchall()

    print(len(results))

    DICT_PEOPLE = dict()
    for item in results:
        url = item.posturl.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
        DICT_PEOPLE[url] = item.username.strip()

    results = engine.execute(f"select id, url, author from jam_post where (username is null or username = '') and author <> 'Alumni'").fetchall()

    print(len(results))

    set_people_no_profile = set()
    for p in tqdm(results):
        url = p.url.replace('http://jam4.sapjam.com', '').replace('https://jam4.sapjam.com', '')
        if url in DICT_PEOPLE.keys():
            engine.execute(f"update jam_post set username = '{DICT_PEOPLE[url]}' where id = {p.id}")
        else:
            set_people_no_profile.add(p.author)

    print('people_no_profile', len(set_people_no_profile))


def clean_dirty_displayname():

    return

if __name__ == '__main__':
    initial_profiles()
    fill_username_people()
    fill_username_post()

    #clean_dirty_displayname()

    print("All Done")