import json
import time
import os

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from timeit import default_timer as timer

from entity import DomainDataSet
from generate import generate_people_cache, get_last_timespot_by_domain

define("port", default=8001, help="nexus backend server", type=int)


class MainHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')

    # def post(self, *args, **kwargs):

    # data = json_decode(self.request.body)
    # engine = create_engine(config.DB_CONNECT_STRING, max_overflow=5)
    # sql = '''select keyword from jam_post'''
    # keyword = engine.execute(sql).fetchall()
    # key = tuple([data['KEYWORD']])
    # if key in keyword:
    #     print("start!!!")
    #     # session = sessionmaker(bind=engine)()
    #     df_contribution, time_spot = get_data(data['KEYWORD'], data['RECENCY_THRESHOLD'], engine)
    #     dataset = generate(data['KEYWORD'], df_contribution, engine, time_spot)
    #     resp = json.dumps(dataset)
    #     self.write(resp)
    # else:
    #     resp = {'status': 404, 'description': 'params error'}
    #     resp = json.dumps(resp)
    #     self.write(resp)

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
            str_data = paras['date'][0].decode("utf-8")
            time_spot = int(time.mktime(time.strptime(str_data, '%Y-%m-%d')))
            if time_spot >= end_time_spot:
                time_spot = end_time_spot
        else:
            time_spot = end_time_spot

        print('time_spot', time_spot)

        if time_spot is None:
            self.write(json.dumps({"state": "success", "data": []}))
            return

        # get from cache json file
        if 'nocache' in paras and paras['nocache'][0].decode("utf-8").upper() != 'TRUE' \
                or 'nocache' not in paras:
            json_file_path = f"./cache/dataset-{domain.lower()}-{str(time_spot)}.json"
            if os.path.exists(json_file_path):
                with open(json_file_path) as json_file:
                    self.write(json.dumps({"state": "cache", "data": json.load(json_file)}))
                    return

        # generate dataset from database
        time_records = dict()
        start = timer()

        ds = DomainDataSet(domain, time_spot)

        ds.set_profiles()
        phase1 = timer()
        time_records["profiles"] = phase1 - start

        if len(ds.profiles) == 0:
            self.write(json.dumps({"state": "success", "time": time_records, "data": []}))
            return

        ds.set_contributions()
        phase2 = timer()
        time_records["contributions"] = phase2 - phase1

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

        resp = {"state": "success",
                "time": time_records,
                "describe": {
                    "profiles": len(ds.profiles),
                    "contributions": len(ds.contributions),
                    "links": len(ds.links),
                    "graph": ds.thresholds,
                    "nodes": len(ds.nodes)
                }, "data": final_result}

        self.write(json.dumps(resp))

    def data_received(self, chunk):
        pass


if __name__ == "__main__":
    generate_people_cache()
    print('Server Started')

    tornado.options.parse_command_line()  # 解析命令行
    app = tornado.web.Application(handlers=[(r'/api/([^\?]*)', MainHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


