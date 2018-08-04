import json
from sqlalchemy import create_engine

import config


def generate_people_cache():
    engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)

    sql = f'''select username, displaynameformatted as displayname, avatar, profileurl, boardarea, functionalarea, 
            costcenter, officelocation, localinfo, email, mobile, managers, reports
            from people_profile where username in (select distinct jam_post.username from jam_post)'''

    people = engine.execute(sql).fetchall()
    print('build cache of people:', len(people))

    results = []

    for p in people:
        if p.username:
            node = dict()
            node["username"] = p.username
            node["displayname"] = p.displayname
            node["avatar"] = p.avatar
            node["profileurl"] = p.profileurl
            node["boardarea"] = p.boardarea
            node["functionalarea"] = p.functionalarea
            node["costcenter"] = p.costcenter
            node["officelocation"] = p.officelocation
            node["localinfo"] = p.localinfo
            node["email"] = p.email
            node["mobile"]  = p.mobile
            node["managers"] = p.managers
            node["reports"] = p.reports

            results.append(node)

    with open(f"./cache/cache-people.json", 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False)


if __name__ == '__main__':
    generate_people_cache()
    print("done")