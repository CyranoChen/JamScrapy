from JamScrapy.mysql import MySQL
import ast

db = MySQL()
results = db.query_dic({
    'select': 'topics',
    'from': 'jam_search_spider'
})

list = []
# results 是140个元素的tuple，每个元素是(str,)
for r in results:
    # r[0]是list格式的字符串，通过eval转成list
    list.extend(ast.literal_eval(r[0]))

# 20*140 = 2800个url
print(len(list))

for url in list:
    # 插入post表
    db.query_dic({
        'insert': 'jam_post_spider',
        'domain_array': [
            'baseurl'
        ],
        'value_array': [
            url
        ]
    })


