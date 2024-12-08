import requests
import json
import time
import random
from bs4 import BeautifulSoup
from datetime import datetime

class BilibiliCommentSpider:
    def __init__(self, video_json_file, t=2, max_retries=3):
        """
        :param video_json_file: 包含视频列表的 JSON 文件路径
        :param t: 请求间隔时间（秒）
        :param max_retries: 请求失败最大重试次数
        """
        self.t = t
        self.max_retries = max_retries
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # 读取视频列表的 JSON 文件
        with open(video_json_file, 'r', encoding='utf-8') as f:
            self.video_data = json.load(f)
        
    def get_comments(self, bv):
        """
        获取视频的评论
        :param bv: 视频的 BV 号
        :return: 评论信息（列表）
        """
        print(f"{bv}\n")
        return None

    def parse_comments(self, comment_data, bv):
        """
        解析评论数据
        :param comment_data: 评论数据的 JSON 格式
        :param bv: 视频的 BV 号
        :return: 返回评论信息的列表，包含评论人、评论内容、评论时间、评论点赞数等
        """
        comments = []
        try:
            video_title = self.get_video_title(bv)
            for comment in comment_data.get('data', {}).get('replies', []):
                comment_info = {
                    'video_title': video_title,
                    'comment_time': self.timestamp_to_datetime(comment['ctime']),
                    'comment_content': comment['content']['message'],
                    'user_name': comment['member']['uname'],
                    'user_is_fan': self.is_user_fan(comment['member']['mid']),
                    'comment_like': comment['like'],
                    'comment_url': f'https://www.bilibili.com/video/{bv}?p={comment["floor"]}',  # 评论的URL
                    'video_like': self.get_video_like_count(bv)
                }
                comments.append(comment_info)
        except Exception as e:
            print(f"Error parsing comments for BV: {bv}, error: {e}")
        return comments

    def get_video_title(self, bv):
        """
        获取视频的标题
        :param bv: 视频的 BV 号
        :return: 视频标题
        """
        video_url = f'https://www.bilibili.com/video/{bv}'
        response = self.session.get(video_url)
        time.sleep(self.t + 2 * random.random())  # 模拟请求间隔
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.find('h1').text.strip()
            return title
        return ""

    def get_video_like_count(self, bv):
        """
        获取视频的点赞数
        :param bv: 视频的 BV 号
        :return: 视频点赞数
        """
        video_url = f'https://www.bilibili.com/video/{bv}'
        response = self.session.get(video_url)
        time.sleep(self.t + 2 * random.random())  # 模拟请求间隔
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            like_count = soup.find('span', {'class': 'like'}).text.strip()
            return int(like_count.replace('万', '0000').replace('万+', '0000'))
        return 0

    def is_user_fan(self, user_id):
        """
        判断评论人是否是该视频的粉丝
        :param user_id: 评论人的用户 ID
        :return: True 如果是粉丝，否则 False
        """
        # 这里可以根据实际需求判断是否为粉丝，可以通过判断用户是否为某个特定用户的粉丝来决定
        return False

    def timestamp_to_datetime(self, timestamp):
        """
        将时间戳转换为 datetime 格式
        :param timestamp: 时间戳
        :return: 转换后的日期时间格式
        """
        return datetime.fromtimestamp(timestamp)

    def get_all_comments(self):
        """
        获取所有视频的评论，返回评论信息
        """
        all_comments = []
        for video in self.video_data:
            bv = video.get('bvid')
            if bv:
                print(f"Fetching comments for BV: {bv}")
                comment_data = self.get_comments(bv)
                if comment_data:
                    comments = self.parse_comments(comment_data, bv)
                    all_comments.extend(comments)
                else:
                    print(f"Failed to retrieve comments for BV: {bv}")
            else:
                print(f"Invalid video entry, missing BV: {video}")
        return all_comments

    def save_comments(self, comments, output_file):
        """保存评论数据"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)


# 示例用法
video_json_file = './QWQ.json'  # 这里是存储视频列表的 JSON 文件路径
spider = BilibiliCommentSpider(video_json_file)

comments = spider.get_all_comments()

# 保存评论数据到文件
spider.save_comments(comments, 'comments_output.json')

# 输出评论
for comment in comments:
    print(f"Video: {comment['video_title']}, Comment: {comment['comment_content']}, User: {comment['user_name']}, Like: {comment['comment_like']}, Time: {comment['comment_time']}, URL: {comment['comment_url']}")
