from JamScrapy.mysql import MySQL


db = MySQL()
results = db.query_dic({
    'select': 'id, baseurl',
    'from': 'jam_post_spider',
    'where': 'body IS NULL'
})

print(results)

for r in results:
    print(r[0])
    print(r[1])