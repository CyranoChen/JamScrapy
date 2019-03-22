# -*- coding: utf-8 -*-
import json
import time
import os
import pandas as pd

from sqlalchemy import text

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from timeit import default_timer as timer

import config
import utils
from entity import DomainDataSet, CommunityStructure, PeopleNetwork
from generate import generate_people_cache, get_last_timespot_by_domain
from photo import generate_face, generate_photo, cvimg_to_base64

define("port", default=8001, help="nexus backend server", type=int)


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def get(self, domain):
        paras = self.request.query_arguments
        if domain is None or domain == "":
            self.write(json.dumps({"state": "exception", "message": "parameter domain is empty"}))
            return

        end_time_spot = get_last_timespot_by_domain(domain)

        if end_time_spot is None:
            self.write(json.dumps({"state": "success", "data": []}))
            return

        if 'date' in paras:
            str_date = paras['date'][0].decode("utf-8")
            time_spot = int(time.mktime(time.strptime(str_date, '%Y-%m-%d')))
            if time_spot >= end_time_spot:
                time_spot = end_time_spot
        else:
            time_spot = end_time_spot

        print('time_spot', time_spot)

        if time_spot is None:
            self.write(json.dumps({"state": "success", "data": []}))
            return

        if 'nonorg' in paras and paras['nonorg'][0].decode("utf-8").upper() == 'TRUE':
            non_org_flag = True
            json_file_path = f"./cache/dataset-{domain.lower()}-{str(time_spot)}-nonorg.json"
        else:
            non_org_flag = False
            json_file_path = f"./cache/dataset-{domain.lower()}-{str(time_spot)}.json"

        print('nonorg', non_org_flag)

        # get from cache json file
        if 'nocache' in paras and paras['nocache'][0].decode("utf-8").upper() != 'TRUE' \
                or 'nocache' not in paras:
            if os.path.exists(json_file_path):
                with open(json_file_path) as json_file:
                    self.write(json.dumps({"state": "cache", "data": json.load(json_file)}))
                    return

        # generate dataset from database
        time_records = dict()
        start = timer()

        ds = DomainDataSet(domain, time_spot, nonorg=non_org_flag)

        ds.set_profiles()
        phase1 = timer()
        time_records["profiles"] = phase1 - start

        if len(ds.profiles) == 0:
            self.write(json.dumps({"state": "success", "time": time_records, "data": []}))
            return

        ds.set_contributions()
        phase2 = timer()
        time_records["contributions"] = phase2 - phase1

        if len(ds.contributions) == 0:
            self.write(json.dumps({"state": "success", "time": time_records, "data": []}))
            return

        ds.set_links()
        phase3 = timer()
        time_records["links"] = phase3 - phase2

        ds.social_analysis()
        phase4 = timer()
        time_records["graph"] = phase4 - phase3

        ds.set_nodes()
        phase5 = timer()
        time_records["nodes"] = phase5 - phase4

        final_result = ds.export_dataset()
        phase6 = timer()
        time_records["export"] = phase6 - phase5

        ds = CommunityStructure(domain, time_spot, nonorg=non_org_flag)

        ds.set_nodes_with_links()
        phase1 = timer()
        time_records["set_nodes_with_links"] = phase1 - start

        ds.community_analysis()
        phase2 = timer()
        time_records["community_analysis"] = phase2 - phase1

        ds.set_node_community_attr()
        phase3 = timer()
        time_records["set_node_community_attr"] = phase3 - phase2

        final_result = ds.export_dataset()
        phase4 = timer()
        time_records["export_dataset"] = phase4 - phase3

        # resp = {"state": "success", "time": time_records, "data": final_result}
        #
        # self.write(json.dumps(resp))

        print('MainHandler done')

        resp = {"state": "success",
                "time": time_records,
                "data": final_result}

        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


class TimeTravelHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def get(self, domain):
        paras = self.request.query_arguments
        if domain is None or domain == "":
            self.write(json.dumps({"state": "exception", "message": "parameter domain is empty"}))
            return

        df = pd.read_csv("./cache/dataset-{}-statistic.csv".format(domain), index_col='month')
        # df = df[:12]
        df = df.sort_index()

        if df is None:
            self.write(json.dumps({"state": "exception", "message": "csv file does not exist"}))
            return

        months = list(df.index)
        nodes = list(df["nodes"])
        links = list(df["links"])
        posts = list(df["posts"])

        assert (len(months) == len(nodes) == len(links) == len(posts))

        print('TimeTravelHandler done')

        resp = {"state": "success", "months": months, "nodes": nodes, "links": links, "posts": posts}

        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


class PeopleNetworkHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def get(self, username):
        paras = self.request.query_arguments
        username = username.upper()
        if username is None or username == "":
            self.write(json.dumps({"state": "exception", "message": "parameter username is empty"}))
            return

        if 'level' in paras:
            str_level = paras['level'][0].decode('utf-8')
            level = int(str_level)

        if 'follow' in paras and paras['follow'][0].decode("utf-8").upper() == 'TRUE':
            follow = True
        else:
            follow = False

        if 'flevel' in paras:
            str_level = paras['flevel'][0].decode('utf-8')
            f_level = int(str_level)
        else:
            f_level = int(level // 1.5)

        if 'slevel' in paras:
            str_level = paras['slevel'][0].decode('utf-8')
            s_level = int(str_level)
        else:
            s_level = int(level // 1.5)

        if follow:
            json_file_path = f"./cache/peoplenetwork-{username}-l{level}-s{s_level}-f{f_level}.json"
        else:
            json_file_path = f"./cache/peoplenetwork-{username}-l{level}-s{s_level}-f0.json"

        # get from cache json file
        if 'nocache' in paras and paras['nocache'][0].decode("utf-8").upper() != 'TRUE' \
                or 'nocache' not in paras:
            if os.path.exists(json_file_path):
                with open(json_file_path) as json_file:
                    self.write(json.dumps({"state": "cache", "data": json.load(json_file)}))
                    return

        # generate dataset from database
        time_records = dict()
        start = timer()

        ds = PeopleNetwork(username, level, s_level, f_level, follow)

        ds.set_links()
        phase1 = timer()
        time_records["links"] = phase1 - start

        ds.set_nodes()
        phase2 = timer()
        time_records["nodes"] = phase2 - phase1

        final_result = ds.export_dataset()
        phase3 = timer()
        time_records["export"] = phase3 - phase2

        print('PeopleNetworkHandler done')

        resp = {"state": "success",
                "time": time_records,
                "data": final_result}

        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


class ProfileCacheHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def get(self, username):
        sql = '''select username, displaynameformatted as displayname from people_profile
                  where username like :username or displayname like :username order by username'''
        results = config.ENGINE.execute(text(sql),
                                        {'username': f'%{username}%', 'displayname': f'%{username}%'}).fetchall()

        print('build cache of people link:', len(results))

        people = [{'id': p.username, 'text': f'[{p.username}] {p.displayname}'} for p in results]

        print('ProfileCacheHandler done')

        resp = {"state": "success", "data": people}

        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


class PhotoLabellingHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def post(self, *args, **kwargs):
        employee = self.get_argument('employee').strip().upper()
        photo = self.request.files['photo'][0]
        # photo = self.get_body_argument('photo')

        if not employee or employee == "" or len(photo) <= 0:
            self.write(json.dumps({"state": "error", "message": "invalid post data"}))
            return

        print('employee:', employee)
        print('photo:', photo)

        try:
            with open(config.PHOTO_FILE_PATH + employee + f'_{str(hash(time.time()))}' +
                      utils.get_file_extension(photo['content_type']), 'wb') as img_file:
                img_file.write(photo['body'])
                img_file.close

            resp = json.dumps({"state": "success", "employee": employee})
            self.write(resp)
        except Exception as e:
            raise e
            self.write(json.dumps({"state": "error", "message": str(e)}))
            return

    def data_received(self, chunk):
        pass


class PhotoFinderHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'GET')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    def get(self, username):
        sql = f"select * from face_extraction where username = :username order by confidence desc "
        results = config.ENGINE.execute(text(sql), {'username': username}).fetchall()

        print('face found:', username, len(results))

        if len(results) <= 0:
            self.write(json.dumps({"state": "error", "message": "no face found"}))
            return

        _list_face_detected = []
        for r in results:
            face = {'id': r.id, 'filepath': r.filepath, 'confidence': r.confidence, 'event': r.event}
            face_img, _ = generate_face(r.filepath, json.loads(r.coordinate))
            face['image'] = str(cvimg_to_base64(face_img), encoding='utf-8')
            _list_face_detected.append(face)

        resp = {"state": "success", "data": _list_face_detected}
        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


if __name__ == "__main__":
    generate_people_cache()
    # generate_relationship_cache()

    print('Server Started')

    tornado.options.parse_command_line()  # 解析命令行
    app = tornado.web.Application(handlers=[(r'/api/([^\?]*)', MainHandler),
                                            (r'/tt/([^\?]*)', TimeTravelHandler),
                                            (r'/pn/([^\?]*)', PeopleNetworkHandler),
                                            (r'/profile/([^\?]*)', ProfileCacheHandler),
                                            (r'/photo/labelling', PhotoLabellingHandler),
                                            (r'/photo/finder/([^\?]*)', PhotoFinderHandler)
                                            ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
