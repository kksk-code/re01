# 该文件实现了爬取Bilibili视频评论的功能。
# 尝试看看能否用字典来存储视频信息，然后遍历字典获取每个视频的评论数据。
#以及查看他的返回的json有没有成功

import requests
from datetime import datetime

class BilibiliCommentScraper:
    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {
            'SESSDATA': 'yours'
        }
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'Content-Type': 'application/json',
        }

    def convert_timestamp_to_readable(self, ctime):
        """将时间戳转换为易懂的日期时间格式"""#方便排序
        timestamp = datetime.fromtimestamp(ctime)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def get_oid_from_bv(self, bv_id):
        """获取视频的 OID (aid)"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
        response = requests.get(api_url, headers=self.headers, cookies=self.cookies)
        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0:
                return data['data']['aid']
        return None

    def get_comments(self, oid, page=1, ps=20):
        """获取视频的评论数据"""
        url = "https://api.bilibili.com/x/v2/reply/main"#comment-api
        params = {
            'type': 1,
            'oid': oid,
            'next': page,
            'ps': ps,
           
        }

        response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'replies' in data['data']:
                return data['data']
        return {}

    def get_replies(self, reply_id, oid):
        """获取评论的回复"""
        url = "https://api.bilibili.com/x/v2/reply/reply"
        params = {
            'oid': oid,
            'type': 1,
            'rpid': reply_id
        }#mode无影响，故删

        response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'replies' in data['data']:
                return data['data']['replies']
        return []

    def print_comments_and_replies(self, bv_id, data):
        """打印评论及其回复，并按照时间排序"""
        print(f"\n视频 BV: {bv_id} 的评论：")

        all_comments = []

        # 获取置顶评论并加入列表
        if 'top_replies' in data:
            top_replies = data['top_replies']
            for top_reply in top_replies:
                name = top_reply['member']['uname']
                sex = top_reply['member']['sex']
                content = top_reply['content']['message']
                like = top_reply['like']
                ctime = top_reply['ctime']
                readable_time = self.convert_timestamp_to_readable(ctime)
                all_comments.append({'name': name, 'sex': sex, 'content': content, 'like': like, 'ctime': ctime, 'readable_time': readable_time, 'type': 'top', 'reply': None})

                # 获取置顶评论的回复
                if 'replies' in top_reply:
                    for reply in top_reply['replies']:
                        reply_name = reply['member']['uname']
                        reply_content = reply['content']['message']
                        reply_like = reply['like']
                        reply_ctime = reply['ctime']
                        readable_reply_time = self.convert_timestamp_to_readable(reply_ctime)
                        all_comments.append({'name': reply_name, 'sex': 'unknown', 'content': reply_content, 'like': reply_like, 'ctime': reply_ctime, 'readable_time': readable_reply_time, 'type': 'reply', 'reply': True})

        # 获取普通评论并加入列表
        for comment in data['replies']:
            name = comment['member']['uname']
            sex = comment['member']['sex']
            content = comment['content']['message']
            like = comment['like']
            ctime = comment['ctime']
            readable_time = self.convert_timestamp_to_readable(ctime)
            all_comments.append({'name': name, 'sex': sex, 'content': content, 'like': like, 'ctime': ctime, 'readable_time': readable_time, 'type': 'normal', 'reply': None})

            # 获取评论的回复
            if 'replies' in comment:
                for reply in comment['replies']:
                    reply_name = reply['member']['uname']
                    reply_content = reply['content']['message']
                    reply_like = reply['like']
                    reply_ctime = reply['ctime']
                    readable_reply_time = self.convert_timestamp_to_readable(reply_ctime)
                    all_comments.append({'name': reply_name, 'sex': 'unknown', 'content': reply_content, 'like': reply_like, 'ctime': reply_ctime, 'readable_time': readable_reply_time, 'type': 'reply', 'reply': True})

        # 按照时间戳排序评论
        all_comments.sort(key=lambda x: x['ctime'])

        # 输出排序后的评论
        for comment in all_comments:
            if comment['type'] == 'top':
                print(f"置顶评论: 昵称: {comment['name']}, 性别: {comment['sex']}, 评论: {comment['content']}, 点赞: {comment['like']}, 时间: {comment['readable_time']}")
            elif comment['type'] == 'normal':
                print(f"普通评论: 昵称: {comment['name']}, 性别: {comment['sex']}, 评论: {comment['content']}, 点赞: {comment['like']}, 时间: {comment['readable_time']}")
            elif comment['type'] == 'reply':
                print(f"  回复: {comment['name']}, 内容: {comment['content']}, 点赞: {comment['like']}, 时间: {comment['readable_time']}")

    def get_multiple_videos_comments(self, bv_ids, total_pages=1):
        """获取多个视频的评论"""
        for bv_id in bv_ids:
            print(f"\n正在获取视频 {bv_id} 的评论...")
            oid = self.get_oid_from_bv(bv_id)
            if oid:
                print(f"视频的 OID: {oid}")
                for page in range(1, total_pages + 1):
                    print(f"正在获取第 {page} 页评论...")
                    data = self.get_comments(oid, page)
                    if data:
                        self.print_comments_and_replies(bv_id, data)
                    else:
                        print(f"第 {page} 页没有评论或请求失败")
            else:
                print(f"无法获取视频 {bv_id} 的 OID")
                #衔接上调取视频列表的代码（jishan。py）返回值是一个字典，键为视频标题，值为BV号
video_dict = {
        "20241201-io茶话会-scoop大师": "BV1pKUkYSEjQ",
        "20241201-io茶话会-heky-从go入手编写属于自己的机器人后端（二）": "BV1C16wYHEzV",
        "20241124-io茶话会-HBill-怎么构建一个排名系统": "BV1GZBbYgEmB"
    }
# 主函数
import json
from datetime import datetime

def main():
    # 字典定义：标题为键，BV号为值
 

    # 创建 BilibiliCommentScraper 实例
    scraper = BilibiliCommentScraper()

    # 初始化结果字典
    results = {}

    # 遍历字典中的视频
    for title, bv_id in video_dict.items():
        print(f"\n正在获取标题为 '{title}' 的视频（BV号: {bv_id}）的评论...")
        oid = scraper.get_oid_from_bv(bv_id)
        if oid:
            print(f"视频的 OID: {oid}")
            comments = []  # 用于存储该视频的格式化评论

            # 获取第一页的评论
            data = scraper.get_comments(oid, page=1)
            if data:
                for reply in data.get("replies", []):
                    # 提取需要的字段
                    comment_data = {
                        "uname": reply["member"]["uname"],
                        "mid": reply["member"]["mid"],
                        "sex": reply["member"]["sex"],
                        "like": reply["like"],
                        "ctime": reply["ctime"],
                        "readable_time": scraper.convert_timestamp_to_readable(reply["ctime"]),
                        "content": reply["content"]["message"],
                        "replies": [
                            {
                                "uname": sub_reply["member"]["uname"],
                                "mid": sub_reply["member"]["mid"],
                                "sex": sub_reply["member"]["sex"],
                                "like": sub_reply["like"],
                                "ctime": sub_reply["ctime"],
                                "readable_time": scraper.convert_timestamp_to_readable(sub_reply["ctime"]),
                                "content": sub_reply["content"]["message"],
                            }
                            for sub_reply in reply.get("replies", [])
                        ],
                        "top": "top_replies" in data and reply in data["top_replies"],
                    }
                    comments.append(comment_data)

            # 将该视频的评论结果存入字典
            results[title] = comments
        else:
            print(f"无法获取标题为 '{title}' 的视频（BV号: {bv_id}）的 OID")

    # 输出结果为 JSON 格式
    print("\n所有评论结果（JSON 格式）：")
    print(json.dumps(results, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()


