from pyecharts.charts import Bar,Line
from pyecharts import options as opts  #配置图表标题等选项
from pyecharts import globals
import json
import requests
import jsonpath
import pymysql
import traceback
import time
def get_conn():
    """
    连接数据库
    :return: 连接，游标
    """
    # 创建连接
    conn = pymysql.connect(host="localhost",
                           user="root",
                           password="123456",
                           db="cov",
                           charset="utf8")
    # 创建游标
    cursor = conn.cursor()  # 执行完毕返回的结果集默认以元组显示
    return conn, cursor

def close_conn(conn, cursor):
    """
    关闭数据库
    :param conn:
    :param cursor:
    :return:
    """
    if cursor:
        cursor.close()
    if conn:
        conn.close()
def insert_foreign_data():
    """
        插入各国疫情数据
    :return:
    """
    cursor = None
    conn = None
    try:
        ls = get_data()[11]  # get_data返回的列标普数据下标为11的数据是给个（国家数据的元组）组成的列表
        print(f"{time.asctime()}开始插入各国数据")
        conn, cursor = get_conn()
        sql = "insert ignore into foreign_data values(%s,%s,%s,%s,%s,%s,%s)" #如果存在这条数据就不插入，如果不存在就插入，避免数据重复
        for i in range(0,len(ls)):
            ds = "2020." + ls[i][4]
            tup = time.strptime(ds, "%Y.%m.%d")
            date = time.strftime("%Y-%m-%d", tup)  # 改变时间格式,不然插入数据库会报错，数据库是datetime类型
            cursor.execute(sql, (date, ls[i][0], ls[i][1], ls[i][2],ls[i][7], ls[i][5], ls[i][9]))


        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}插入数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def get_globalStatis_data():
    url = 'https://view.inews.qq.com/g2/getOnsInfo?name=disease_foreign'
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    r = requests.get(url, headers)
    res = json.loads(r.text)  # json字符串转字典
    data_all = json.loads(res['data'])
    lastUpdateTime = data_all['globalStatis']['lastUpdateTime']  # YYYY-MM-DD HH:mm:ss
    nowConfirm = data_all['globalStatis']['nowConfirm']
    confirm = data_all['globalStatis']["confirm"]
    heal = data_all['globalStatis']["heal"]
    dead = data_all['globalStatis']["dead"]
    nowConfirmAdd = data_all['globalStatis']['nowConfirmAdd']
    confirmAdd = data_all['globalStatis']['confirmAdd']
    healAdd = data_all['globalStatis']['healAdd']
    deadAdd = data_all['globalStatis']['deadAdd']
    globalStatis = {"lastUpdateTime": lastUpdateTime, "nowConfirm": nowConfirm, "confirm": confirm, "heal": heal,
                        "dead": dead,
                        "nowConfirmAdd": nowConfirmAdd, "confirmAdd": confirmAdd, "healAdd": healAdd,
                        "deadAdd": deadAdd}
    return globalStatis

def insert_globalStatis():
    """
        插入全球疫情数据
    :return:
    """
    cursor = None
    conn = None
    try:
        dict = get_globalStatis_data()  #  全球数据字典
        print(f"{time.asctime()}开始插入全球数据")
        conn, cursor = get_conn()
        sql = "insert ignore into globalStatis values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"

        cursor.execute(sql, (dict['lastUpdateTime'], dict['nowConfirm'], dict['confirm'], dict['heal'],dict['dead'], dict['nowConfirmAdd'], dict['confirmAdd'],dict['healAdd'],dict['deadAdd']))


        conn.commit()  # 提交事务 update delete insert操作
        print(f"{time.asctime()}插入数据完毕")
    except:
        traceback.print_exc()
    finally:
        close_conn(conn, cursor)

def get_data ():
    # 1.目标网站
    url = 'https://api.inews.qq.com/newsqa/v1/automation/foreign/country/ranklist'
    # 2.请求资源
    resp = requests.get(url)
    # print(resp.text)
    # 3.提取数据
    # 类型转换 json-->dict
    data = json.loads(resp.text)
    # print(type(data))
    # for i in range(0,len(data['data'])) :
    #     print(data['data'][i]['name'])
    # data是我们的内容，$表示根节点下，而$..name表示根节点下的任意层级name键值的部分
    name = jsonpath.jsonpath(data, "$..name")#JsonPath是一种简单的方法来提取给定JSON文档的部分内容
    confirm = jsonpath.jsonpath(data, "$..confirm")
    confirmAdd = jsonpath.jsonpath(data, "$..confirmAdd")
    confirmCompare = jsonpath.jsonpath(data, "$..confirmCompare")
    date = jsonpath.jsonpath(data, "$..date")
    dead = jsonpath.jsonpath(data, "$..dead")
    deadCompare = jsonpath.jsonpath(data, "$..deadCompare")
    heal = jsonpath.jsonpath(data, "$..heal")
    healCompare = jsonpath.jsonpath(data, "$..healCompare")
    nowConfirm = jsonpath.jsonpath(data, "$..nowConfirm")
    nowConfirmCompare = jsonpath.jsonpath(data, "$..nowConfirmCompare")
    data_list = list(zip(name,confirm,confirmAdd,confirmCompare,date,dead,deadCompare,heal,healCompare,nowConfirm,nowConfirmCompare))
    return [name,confirm,confirmAdd,confirmCompare,date,dead,deadCompare,heal,healCompare,nowConfirm,nowConfirmCompare,data_list]



def Top5():
    bar = Bar()
    bar.set_global_opts(xaxis_opts=opts.AxisOpts(name='国家'),yaxis_opts=opts.AxisOpts(name='人数'),legend_opts=opts.LegendOpts(pos_top='0%',pos_left='right')
                        ,title_opts=opts.TitleOpts(title='严重程度前5名国家疫情数据显示',subtitle='\n数据来源：腾讯',subtitle_link='https://xw.qq.com/act/qgfeiyan?pgv_ref=3gqtb&ADTAG=3gqtb',pos_left='center'))
    bar.page_title = '严重程度前5名国家疫情数据显示'
    bar.height = '600px'
    bar.width = '100%'
    bar.add_xaxis(get_data()[0][0:5])
    bar.add_yaxis("确诊", get_data()[1][0:5])
    bar.add_yaxis("治愈", get_data()[7][0:5])
    bar.add_yaxis("死亡", get_data()[5][0:5])
    bar.add_yaxis("现存确诊", get_data()[9][0:5])
    bar.add_yaxis("新增确诊", get_data()[2][0:5])
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    # 也可以传入路径参数，如 bar.render("mycharts.html")
    bar.render('Top5.html')

def globalStatis():
    bar1 = Bar()
    bar1.set_global_opts(xaxis_opts=opts.AxisOpts(name='日期'), yaxis_opts=opts.AxisOpts(name='人数'),
                        legend_opts=opts.LegendOpts(pos_top='0%', pos_left='right')
                        , title_opts=opts.TitleOpts(title='全球疫情数据显示', subtitle='\n数据来源：腾讯',
                                                    pos_left='center'))
    bar1.page_title = '全球疫情数据显示'
    bar1.height = '600px'
    bar1.width = '100%'
    bar1.add_xaxis([get_globalStatis_data()['lastUpdateTime']])
    bar1.add_yaxis('确诊',[get_globalStatis_data()['confirm']])
    bar1.add_yaxis('治愈',[get_globalStatis_data()['heal']])
    bar1.add_yaxis("死亡",[get_globalStatis_data()['dead']])
    bar1.add_yaxis("现存确诊",[get_globalStatis_data()['nowConfirm']])
    bar1.add_yaxis("新增确诊",[get_globalStatis_data()['confirmAdd']])
    # render 会生成本地 HTML 文件，默认会在当前目录生成 render.html 文件
    # 也可以传入路径参数，如 bar.render("mycharts.html")
    bar1.render('globalStatis.html')

insert_foreign_data()
insert_globalStatis()
Top5()
globalStatis()
