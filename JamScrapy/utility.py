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
