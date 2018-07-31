import json
import time
import datetime

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from timeit import default_timer as timer

from entity import DomainDataSet

define("port", default=8001, help="run on the given port", type=int)


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
        if 'date' in paras:
            str_data = paras['date'][0].decode("utf-8")
            time_spot = int(time.mktime(time.strptime(str_data, '%Y-%m-%d')))
        else:
            now = datetime.datetime.now()
            time_spot = int(time.mktime(time.strptime(now.strftime("%Y-%m-%d 00:00:00"), '%Y-%m-%d %H:%M:%S')))

        time_records = dict()
        start = timer()

        ds = DomainDataSet(domain, time_spot)

        ds.set_profiles()
        phase1 = timer()
        time_records["profiles"] = phase1 - start

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

        resp = {"time": time_records,
                "describe": {
                    "profiles": len(ds.profiles),
                    "contributions": len(ds.contributions),
                    "links": len(ds.links),
                    "graph": ds.thresholds,
                    "nodes": len(ds.nodes)
                }, "data": final_result}
        resp = json.dumps(resp)

        self.write(resp)

    def data_received(self, chunk):
        pass


if __name__ == "__main__":
    tornado.options.parse_command_line()  # 解析命令行
    app = tornado.web.Application(handlers=[(r'/api/([^\?]*)', MainHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
