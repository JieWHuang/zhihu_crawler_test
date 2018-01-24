import json
import new_zhihu_common
from new_zhihu_common import mydb

topic_begin_url = 'https://www.zhihu.com/api/v4/topics/'

question_level = 1
limit = 5
max_offset = 20  # 最大为1000


def get_zhihu_topic_id():
    for item in mydb['zhihu_topic_list'].find():
        if item['topic_level'] == question_level:
            yield item['topic_id'], item['topic_name']


def get_zhihu_question(url, topic_id, topic_name):
    html = new_zhihu_common.get(url)
    json_data = json.loads(html)
    try:
        for item in json_data['data']:
            if item['target'].get('question'):
                question_title = item['target']['question']['title']
                question_id = item['target']['question']['id']
                zhihu_question_info = {
                    'type': item['target']['question']['type'],
                    'question_title': question_title,
                    'question_id': question_id,
                    'topic_name': topic_name,
                    'topic_id': topic_id
                }
                print(zhihu_question_info)
            elif item['target'].get('column'):
                column_title = item['target']['column']['title']
                column_id = item['target']['column']['id']
                author_name = item['target']['column']['author']['name']
                author_url_token = item['target']['column']['author']['url_token']
                column_info = {
                    'type': item['target']['column']['type'],
                    'column_title': column_title,
                    'column_id': column_id,
                    'topic_name': topic_name,
                    'topic_id': topic_id,
                }
                print(column_info)
                user_info = {
                    'type':item['target']['column']['author']['type'],
                    'author_name': author_name,
                    'author_url_token': author_url_token
                }
                print(user_info)

    except:
        pass


def get_zhihu_question_list():
    for topic_id, topic_name in get_zhihu_topic_id():
        for offset in range(0, max_offset, limit):
            url = topic_begin_url + '{}/feeds/essence?limit={}&offset={}'.format(topic_id, limit, offset)
            get_zhihu_question(url, topic_id, topic_name)


def save_zhihu_question_list(data):
    try:
        if mydb['zhihu_question_list'].update({'question_id': data['question_id']}, {'$set': data},
                                              True):  # 保存到MongoDB数据库，重复的则不保存
            print(data['question_title'], 'Saving to MongoDB...')
        else:
            print(data['question_title'], 'Saving to MongoDB Failed')
    except:
        pass


def main():
    get_zhihu_question_list()


if __name__ == '__main__':
    main()
