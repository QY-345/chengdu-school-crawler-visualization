import requests
from lxml import etree
import time
import pymysql
import re



def web_request():
    try:
        session = requests.Session()

        url = "https://infomap.cdedu.com/Home/Index"
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
            "upgrade-insecure-requests": "1",
        }
        school_list = []
        for i in range(1, 44):
            params = {
                "all": "1",
                "per": "b4152536-3c7d-46a6-9738-93e237d985ce",
                "nat": "73b80ebb-74c8-4cc2-89b0-36e6c977b96d",
                "pages": f"{i}"

            }
            cookie = {"ASP.NET_SessionId": "thdrh1obwfn3fwoesd5vfmut"}
            response = session.get(url=url, headers=headers, params=params, cookies=cookie)
            datas_text = etree.HTML(response.text)
            datas = datas_text.xpath('//div[@class="index1"]//ul')
            # print(datas)

            for data in datas:
                # print(data.xpath('./li'))
                for info in data.xpath('./li'):
                    # print(info)
                    school_name = info.xpath('./a//h1/text()')[0]
                    school_text = info.xpath('./div[@class="text_div"]/p/text()')
                    # print(school_name, school_text)

                    stage = school_text[0].strip() if len(school_text) > 0 else ""
                    area = school_text[1].strip() if len(school_text) > 1 else ""
                    classes = school_text[2].strip() if len(school_text) > 2 else ""
                    address = school_text[3].strip() if len(school_text) > 3 else None
                    school_list.append([school_name, stage, area, classes, address])

            time.sleep(1)
        # print(school_list)
        # print(len(school_list))
        return school_list

    except Exception as e:
        print("爬取失败", e)
        return False


def set_mysql_tables():
    db = pymysql.connect(host='localhost', user='root', passwd='quying250028asd', port=3306)
    print("连接成功")
    # 创建游标对象
    cursor = db.cursor()
    # 创建数据库，以及数据库编码和排列顺序
    cursor.execute("create database if not exists school_data character set utf8mb4 collate utf8mb4_general_ci")
    cursor.execute("show databases")
    print(cursor.fetchall())
    cursor.execute("use school_data")
    set_tables = """create table if not exists school_info
     (
    id int auto_increment primary key comment "学校编号",
    name varchar(100) comment "学校名字",
    stage varchar(100) comment "学段",
    area varchar(100) comment "所在区域",
    classes varchar(100) comment "办学类型",
    address varchar(100)  comment "详细地址"
    )
    """
    cursor.execute(set_tables)
    cursor.execute("show tables")
    print(cursor.fetchall())
    try:
        # 1. 检查表格是否有数据
        cursor.execute("SELECT COUNT(*) FROM school_info")
        record_count = cursor.fetchone()[0]  # 获取记录总数
        print(f"当前表中数据条数：{record_count}")

        # 2. 如果有数据，则清空表
        if record_count > 0:
            # 推荐用TRUNCATE（效率高，重置自增ID）
            cursor.execute("TRUNCATE TABLE school_info")
            print("表格不为空，已清空数据")
            print("重新插入数据")

            # 插入数据
            for i in web_request():
                sql = """
                            INSERT INTO school_info (name, stage, area, classes, address)  VALUES (%s, %s, %s, %s, %s)            
                          """
                cursor.execute(sql, (i[0], i[1], i[2], i[3], i[4]))

            db.commit()
            print("插入成功")
            cursor.close()
        else:
            print("表格为空，无需清空")

            # 插入数据
            for i in web_request():
                sql = """
                INSERT INTO school_info (name, stage, area, classes, address)  VALUES (%s, %s, %s, %s, %s)            
                """
                cursor.execute(sql, (i[0], i[1], i[2], i[3], i[4]))
            db.commit()
            print("插入成功")
            cursor.close()

    except Exception as e:
        print(e)


def mysql_data():
    db = pymysql.connect(host='localhost', user='root', passwd='quying250028asd', port=3306, database='school_data')
    print("连接成功")
    # 创建游标对象
    cursor = db.cursor()
    cursor.execute("show tables")
    # print(cursor.fetchall())
    cursor.execute("select * from school_info")
    # print(cursor.fetchall())
    cursor.execute("select distinct area from school_info where area regexp '^【区域】'")
    raw_areas = [item[0] for item in cursor.fetchall()]  # 转换为列表：['【区域】市直属直管学校', ...]
    # print(raw_areas)
    # print(len(raw_areas))
    cursor.execute("select * from school_info")
    areas_list = []
    for i in raw_areas:
        a = re.match(r"【区域】(.*)", i).group(1)
        areas_list.append(a)
    print(areas_list)
    # print(len(areas_list))
    # 统计数量

    count_list = []
    cursor.execute("select area from school_info where area regexp '^【区域】'")
    all_list = cursor.fetchall()
    # print(all_list)
    for r in raw_areas:
        count = 0
        for e in all_list:
            if e[0] == r:
                count += 1
        count_list.append(count)
    print(count_list)
    cursor.close()
    return areas_list, count_list


if __name__ == '__main__':
    mysql_data()
