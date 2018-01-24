import json
import new_zhihu_common
import time

start_url = 'https://www.zhihu.com/topic/19776749/organize/entire'
max_level = 3


def get_first_level_topic_url(url):  # 广度优先遍历根话题下第一层话题
    topic_level = 1  # 设置第一层话题的深度为1
    html = new_zhihu_common.post(url)  # 知乎话题树的请求方式是POST
    json_data = json.loads(html)  # 解析json网页内容
    for item in json_data['msg'][1]:
        topic_name = item[0][1]  # 话题名称
        topic_id = item[0][2]  # 话题id
        if topic_id != '19776751':  # 「未归类」话题，多是话题别名，不作考虑
            topic_info = {
                'type': item[0][0],
                'topic_name': topic_name,
                'topic_id': topic_id,
                'topic_level': topic_level,
                'parent_topic_name': json_data['msg'][0][1],
                'parent_topic_id': json_data['msg'][0][2]
            }
            print(topic_info)
            new_zhihu_common.save2mongodb(topic_info, topic_info['type'])
            yield start_url + '?child=&parent={}'.format(topic_id), topic_level + 1  # 生成第二层话题的地址和深度


def get_topic_info(url, topic_level):  # 深度优先遍历
    # time.sleep(1)
    try:
        if topic_level <= max_level:  # 判断话题爬虫深度
            html = new_zhihu_common.post(url)
            json_data = json.loads(html)
            for item in json_data['msg'][1]:
                topic_name = item[0][1]
                topic_id = item[0][2]
                if topic_name != '加载更多':  # 负责处理话题信息
                    topic_info = {
                        'type': item[0][0],
                        'topic_name': topic_name,
                        'topic_id': topic_id,
                        'topic_level': topic_level,
                        'parent_topic_name': json_data['msg'][0][1],
                        'parent_topic_id': json_data['msg'][0][2]
                    }
                    print(topic_info)
                    new_zhihu_common.save2mongodb(topic_info, topic_info['type'])
                if item[0][1] == '加载更多':  # 负责翻页，实现广度遍历
                    next_page_url = start_url + '?child={}&parent={}'.format(item[0][2], item[0][3])
                    get_topic_info(next_page_url, topic_level)
                else:
                    if len(item) == 2:  # 判断是否有'显示子话题'，有则递归调用本身，实现深度遍历
                        child_topic_url = start_url + '?child=&parent={}'.format(item[0][2])
                        child_topic_level = topic_level + 1
                        get_topic_info(child_topic_url, child_topic_level)
    except:
        print('Get_Topic_Info Error!')  # 若发生异常，则重新调用方法


def main():
    for url, topic_level in get_first_level_topic_url(start_url):
        get_topic_info(url, topic_level)


if __name__ == '__main__':
    main()
