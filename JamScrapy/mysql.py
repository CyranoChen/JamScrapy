import pymysql


class MySQL:
    __db = None

    # 在这里配置自己的SQL服务器
    # set global max_allowed_packet = 2*1024*1024*10
    __config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'passwd': 'Linfeng01!',
        'db': 'scrapy',
        # utf8 -> utf8mb4 针对互联网emoji表情符号，修改编码
        'charset': 'utf8mb4'
    }

    def __init__(self):
        self.__connect()

    def __del__(self):
        if self.__db is not None:
            self.__db.close()

    def __connect(self):
        if self.__db is None:
            self.__db = pymysql.connect(**self.__config)
        return self.__db

    def escape_string(self, _str):
        return self.__db.escape_string(_str)

    def query(self, _sql):
        cursor = self.__connect().cursor()
        try:
            cursor.execute(_sql)
            data = cursor.fetchall()
            # 提交到数据库执行
            self.__connect().commit()
        except (BaseException) as e:
            # 如果发生错误则回滚
            self.__connect().rollback()
            print(e)
            return False
        return data

    def query_dic(self, _sql_dic):
        if 'select' in _sql_dic.keys():
            sql = "SELECT " + _sql_dic['select'] + " FROM " + _sql_dic['from']
            if 'where' in _sql_dic.keys():
                sql += self.where(_sql_dic['where'])
            print(sql)
            return self.query(sql)
        elif 'insert' in _sql_dic.keys():
            sql = "INSERT INTO " + _sql_dic['insert'] + self.quote(_sql_dic['domain_array'], type_filter=False) \
                  + " VALUES " + self.quote(_sql_dic['value_array'])
            print(sql)
            return self.query(sql)
        if 'delete' in _sql_dic.keys():
            sql = "DELETE FROM " + _sql_dic['delete'] + self.where(_sql_dic['where'])
            print(sql)
            return self.query(sql)

    def where(self, _sql):
        if not isinstance(_sql, dict):
            return " WHERE " + str(_sql)
        if isinstance(_sql, dict):
            _sql_dic = _sql
            s = " WHERE "
            index = 0
            for domain in _sql_dic:
                if index == 0:
                    s += domain + "=" + str(_sql_dic[domain]) + " "
                    index += 1
                else:
                    s += "AND " + domain + "=" + str(_sql_dic[domain]) + " "
            return s

    # 为数组加上外括号，并拼接字符串
    def quote(self, _data_array, type_filter=True):
        s = "("
        index = 0
        if type_filter:
            for domain in _data_array:
                if index == 0:
                    if isinstance(domain, int):
                        s += str(domain)
                    elif isinstance(domain, str):
                        s += "'" + domain + "'"
                    index += 1
                else:
                    if isinstance(domain, int):
                        s += ", " + str(domain)
                    elif isinstance(domain, str):
                        s += ", " + "'" + domain + "'"
        else:
            for domain in _data_array:
                if index == 0:
                    s += str(domain)
                    index += 1
                else:
                    s += ", " + domain
        return s + ")"
