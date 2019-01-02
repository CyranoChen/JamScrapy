import json


def max_min_normalize(x):
    x = (x - x.min()) / (x.max() - x.min());
    return x;


def build_profileurl_dict(profiles):
    profileurl_dict = dict()

    for p in profiles:
        if p.profileurl:
            url = p.profileurl.split('/')[-1]
            profileurl_dict[url] = p.username.strip()
        else:
            print(p)

    return profileurl_dict


def get_people_username(profileurl):
    url = profileurl.split('/')[-1]

    if len(PROFILE_URL) > 0 and url in PROFILE_URL.keys():
        return PROFILE_URL[url]
    else:
        return ''


def generate_relation(list, filters, str, source=None, target=None, role=None, ban=False):
    if str:
        jsons = json.loads(str)
        if not ban or ban and (len(jsons) <= LINKS_THRESHOLD):
            for item in jsons:
                url = item['url']
                name = get_people_username(url)
                if (name in filters) and (name not in BLACK_LIST) and name != '':
                    if source is not None:
                        list.append({"source": source, "target": name, "role": role})
                    elif target is not None:
                        list.append({"source": name, "target": target, "role": role})


def get_people_contribution(username):
    item = df[df['username'] == username]
    if item.size > 0:
        return float(item['contribution']);
    else:
        return 0;


def get_people_indicators(username, key):
    item = df[df['username'] == username]
    if item.size > 0 and key in item.keys():
        return int(item[key])
    else:
        return 0;


def get_people_network_degree(username):
    if username in nodes_degree.keys():
        return int(nodes_degree[username])
    else:
        return 0;


def get_people_network_type(username):
    item = df[df['username'] == username]
    # print(item, item.betweenness)
    if float(item.betweenness) >= betweenness_threshold:
        return 'Brokers'
    elif float(item.closeness) >= closeness_threshold:
        return 'Influencers'
    elif float(item.degree) >= degree_threshold:
        return 'Connectors'
    else:
        return 'Soloists'

    return 'Soloists'


import matplotlib.pyplot as plt


def plt_pie(values, labels):
    # 设置绘图的主题风格（不妨使用R中的ggplot分隔）  
    plt.style.use('ggplot')

    # explode = [0,0,0,0,0,0,0,0,0,0]  # 用于突出显示
    # colors=['#ff8888','#88ff88','#333333','#dddddd','#8888ff'] # 自定义颜色

    # 中文乱码和坐标轴负号的处理  
    plt.rcParams['font.sans-serif'] = ['Verdana']
    plt.rcParams['axes.unicode_minus'] = False

    # 将横、纵坐标轴标准化处理，保证饼图是一个正圆，否则为椭圆  
    plt.axes(aspect='equal')

    # 控制x轴和y轴的范围  
    plt.xlim(0, 4)
    plt.ylim(0, 4)

    # 绘制饼图  
    plt.pie(x=values,  # 绘图数据
            # explode=explode, # 突出显示
            labels=labels,  # 添加标签
            # colors=colors, # 设置饼图的自定义填充色
            autopct='%.2f%%',  # 设置百分比的格式，这里保留一位小数
            pctdistance=0.6,  # 设置百分比标签与圆心的距离  
            labeldistance=1.2,  # 设置教育水平标签与圆心的距离
            startangle=180,  # 设置饼图的初始角度
            radius=1.5,  # 设置饼图的半径
            counterclock=False,  # 是否逆时针，这里设置为顺时针方向
            wedgeprops={'linewidth': 1.5, 'edgecolor': 'white'},  # 设置饼图内外边界的属性值
            textprops={'fontsize': 12, 'color': 'k'},  # 设置文本标签的属性值
            center=(1.8, 1.8),  # 设置饼图的原点
            frame=0)  # 是否显示饼图的图框，这里设置显示

    # 删除x轴和y轴的刻度  
    plt.xticks(())
    plt.yticks(())
    # 添加图标题  
    # plt.title('')

    # 显示图形  
    plt.show()
