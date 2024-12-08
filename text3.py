#defeat，废弃接口
#有的时候是因为api接口不稳定，所以爬不出来信息，与ip被封无关，与程序写的有一点关系
#本代码尝试抓取用户ID为436623527的视频列表（我的）
import json
import re
import time
import requests
'''API 错误: 请求过于频繁，请稍后再试
所有视频数据抓取完毕。
视频数据已保存到 url.json 文件中。
共抓取到 0 个视频。'''

class GetInfo:
    def __init__(self, user_id):
        """
        初始化对象，设置用户 ID 和请求头
        """
        self.user_id = user_id
        self.a_list = []  # 存储每一个视频的信息
        self.base_url = f"https://api.bilibili.com/x/space/arc/search"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Cookie": "b4c46ab5%2C1748612005%2C9a2d8%2Ac1CjCw",  # 替换为你的 SESSDATA
        }

    def get_videos_by_page(self, page):
        """
        获取某一页的视频数据
        :param page: 页码
        :return: 当前页视频数据的列表
        """
        params = {
            "mid": self.user_id,  # 用户 ID
            "ps": 30,             # 每页视频数量
            "pn": page,           # 页码
            "jsonp": "jsonp",     # 响应格式
        }
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()
            
            if data.get("code") != 0:
                print(f"API 错误: {data.get('message')}")
                return []

            video_list = data.get("data", {}).get("list", {}).get("vlist", [])
            return [
                {
                    "title": video.get("title"),
                    "aid": video.get("aid"),
                    "bvid": video.get("bvid"),
                    "url": f"https://www.bilibili.com/video/{video.get('bvid')}"
                }
                for video in video_list
            ]

        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            return []

    def get_all_videos(self):
        """
        遍历所有页面获取视频数据
        """
        page = 1
        while True:
            print(f"正在获取第 {page} 页...")
            videos = self.get_videos_by_page(page)
            if not videos:  # 没有更多数据时退出
                print("所有视频数据抓取完毕。")
                break
            self.a_list.extend(videos)
            page += 1
            time.sleep(2)  # 避免请求过于频繁

        return self.a_list

    def save_to_file(self):
        """
        保存结果到 JSON 文件
        """
        with open("url.json", "w", encoding="utf-8") as f:
            json.dump(self.a_list, f, ensure_ascii=False, indent=4)
        print("视频数据已保存到 url.json 文件中。")


# 用户 ID
USER_ID = 436623527

# 初始化并爬取数据
spider = GetInfo(USER_ID)
video_list = spider.get_all_videos()

# 保存到文件
spider.save_to_file()

print(f"共抓取到 {len(video_list)} 个视频。")
