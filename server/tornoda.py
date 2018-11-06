import json
import time
import os
import pandas as pd

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from timeit import default_timer as timer

from entity import DomainDataSet, CommunityStructure
from generate import generate_people_cache, get_last_timespot_by_domain

define("port", default=8001, help="nexus backend server", type=int)


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
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
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
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


# class CommunityStructrueHandler(tornado.web.RequestHandler):
#     def set_default_headers(self):
#         self.set_header('Access-Control-Allow-Origin', '*')
#         self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
#         self.set_header('Access-Control-Allow-Headers', '*')
#         self.set_header('Content-type', 'application/json')
#
#     def get(self, domain):
#         paras = self.request.query_arguments
#         if domain is None or domain == "":
#             self.write(json.dumps({"state": "exception", "message": "parameter domain is empty"}))
#             return
#
#         end_time_spot = get_last_timespot_by_domain(domain)
#
#         if end_time_spot is None:
#             self.write(json.dumps({"state": "success", "data": []}))
#             return
#
#         if 'date' in paras:
#             str_date = paras['date'][0].decode("utf-8")
#             time_spot = int(time.mktime(time.strptime(str_date, '%Y-%m-%d')))
#             if time_spot >= end_time_spot:
#                 time_spot = end_time_spot
#         else:
#             time_spot = end_time_spot
#
#         print('time_spot', time_spot)
#
#         if time_spot is None:
#             self.write(json.dumps({"state": "success", "data": []}))
#             return
#
#         json_file_path = f"./cache/dataset-{domain.lower()}-{str(time_spot)}.json"
#         if not os.path.exists(json_file_path):
#             self.write(json.dumps({"state": "exception", "message": "no data source file cached"}))
#             return
#
#         # get from cache json file
#         if 'nocache' in paras and paras['nocache'][0].decode("utf-8").upper() != 'TRUE' \
#                 or 'nocache' not in paras:
#             # generate dataset from cache file
#             with open(json_file_path) as json_file:
#                 ds = json.load(json_file)
#                 if 'community' in ds['nodes'][0]:
#                     # return directly
#                     self.write(json.dumps({"state": "cache", "data": ds}))
#                     return
#
#         # handle the dataset to add attr community
#         time_records = dict()
#         start = timer()
#
#         ds = CommunityStructure(domain, time_spot)
#
#         ds.set_nodes_with_links()
#         phase1 = timer()
#         time_records["set_nodes_with_links"] = phase1 - start
#
#         ds.community_analysis()
#         phase2 = timer()
#         time_records["community_analysis"] = phase2 - phase1
#
#         ds.set_node_community_attr()
#         phase3 = timer()
#         time_records["set_node_community_attr"] = phase3 - phase2
#
#         final_result = ds.export_dataset()
#         phase4 = timer()
#         time_records["export_dataset"] = phase4 - phase3
#
#         print('CommunityStructrueHandler done')
#
#         resp = {"state": "success", "time": time_records, "data": final_result}
#
#         self.write(json.dumps(resp))
#
#     def data_received(self, chunk):
#         pass


if __name__ == "__main__":
    generate_people_cache()
    print('Server Started')

    tornado.options.parse_command_line()  # 解析命令行
    app = tornado.web.Application(handlers=[(r'/api/([^\?]*)', MainHandler),
                                            (r'/tt/([^\?]*)', TimeTravelHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
