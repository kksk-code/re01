#defeat
#是comment和video_data合并在一起的代码
#也是用的那个废弃的api接口
#24.12.5
import argparse
import requests
import time
import random
import json
from datetime import datetime
import os


class BilibiliCommentScraper:
    def __init__(self, cookies=None, headers=None):
        self.cookies = cookies or {
            'SESSDATA': 'your_sessdata_here'
        }
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Content-Type': 'application/json',
        }

    def convert_timestamp_to_readable(self, ctime):
        """将时间戳转换为易懂的日期时间格式"""
        timestamp = datetime.fromtimestamp(ctime)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def get_videos(self, uid, page_size=30):
        """获取指定用户的所有视频列表并按时间先后排序"""
        base_url = "https://api.bilibili.com/x/space/arc/search"
        videos = []
        page = 1

        while True:
            print(f"正在抓取第 {page} 页数据...")
            params = {
                "mid": uid,
                "ps": page_size,
                "pn": page,
                "tid": 0,
                "keyword": "",
                "order": "pubdate",
                "jsonp": "jsonp"
            }
            try:
                response = requests.get(base_url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()

                # 检查是否有视频列表
                video_list = data.get("data", {}).get("list", {}).get("vlist", [])
                if not video_list:
                    print("所有视频数据抓取完毕。")
                    break

                for video in video_list:
                    videos.append({
                        "title": video.get("title"),
                        "bvid": video.get("bvid"),
                        "aid": video.get("aid"),
                        "created": video.get("created"),
                        "created_readable": self.convert_timestamp_to_readable(video.get("created")),
                        "url": f"https://www.bilibili.com/video/{video.get('bvid')}"
                    })

                # 下一页
                page += 1

                # 随机延时 1 到 3 秒
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"抓取时出现错误：{e}")
                break

        # 按时间先后排序（升序）
        videos.sort(key=lambda x: x["created"])
        return videos

    def get_comments(self, oid, page=1, ps=20):
        """获取视频的评论数据"""
        url = "https://api.bilibili.com/x/v2/reply/main"
        params = {
            'type': 1,
            'oid': oid,
            'next': page,
            'ps': ps,
            'mode': 3
        }

        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and 'replies' in data['data']:
                    return data['data']
        except Exception as e:
            print(f"获取评论时出现错误：{e}")
        return {}

    def save_to_file(self, filename, new_data):
        """实时更新保存数据到文件"""
        if os.path.exists(filename):
            # 读取已有文件
            with open(filename, 'r', encoding='utf-8') as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # 检查新数据是否已经存在
        updated_data = existing_data
        for video in new_data:
            if video not in existing_data:
                updated_data.append(video)

        # 写回文件
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(updated_data, file, ensure_ascii=False, indent=4)
        print(f"数据已实时保存到 {filename}")

    def process_videos_and_comments(self, uid, total_pages=1, filename="bilibili_data.json"):
        """抓取用户视频并获取每个视频的评论"""
        videos = self.get_videos(uid)

        if videos:
            print(f"共抓取到 {len(videos)} 个视频。")
            for video in videos:
                bv_id = video['bvid']
                created_time = video['created_readable']
                print(f"\n正在获取视频《{video['title']}》（发布于 {created_time}）的评论...")
                video_data = {
                    "title": video['title'],
                    "bvid": video['bvid'],
                    "created": video['created_readable'],
                    "url": video['url'],
                    "comments": []
                }
                for page in range(1, total_pages + 1):
                    print(f"正在获取第 {page} 页评论...")
                    data = self.get_comments(video['aid'], page)
                    if data and "replies" in data:
                        for comment in data['replies']:
                            video_data["comments"].append({
                                "user": comment['member']['uname'],
                                "content": comment['content']['message'],
                                "likes": comment['like'],
                                "time": self.convert_timestamp_to_readable(comment['ctime'])
                            })
                    else:
                        print(f"第 {page} 页没有评论或请求失败")
                    
                    # 随机延时 2 到 5 秒
                    time.sleep(random.uniform(2, 5))
                self.save_to_file(filename, [video_data])
        else:
            print("未找到任何视频。")


# 主函数
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抓取指定用户的所有视频列表和评论")
    parser.add_argument("--uid", type=str, required=True, help="用户ID (必填参数)")
    parser.add_argument("--pages", type=int, default=1, help="每个视频评论的页数")
    parser.add_argument("--filename", type=str, default="bilibili_data.json", help="保存数据的文件名")
    args = parser.parse_args()

    scraper = BilibiliCommentScraper()
    scraper.process_videos_and_comments(args.uid, args.pages, args.filename)

''''''