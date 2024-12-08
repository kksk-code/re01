#实现从字典（键名标题，键值BV号）中获取BV号，
# 获取视频的OID，获取评论数据，整理评论数据，打印评论数据。
#12.5.2024
#一次爬过就显示{'code': -400, 'message': '请求错误', 'ttl': 1}
#应该是接口不稳定，因为用这个api写的其他代码也显示爬不出信息
import requests，
import json
from datetime import datetime
from typing import List, Dict, Union, Optional

class BilibiliCommentScraper:
    def __init__(self, cookies: Optional[Dict[str, str]] = None, headers: Optional[Dict[str, str]] = None):
        self.cookies = cookies or {'SESSDATA': 'xxx'}
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
            'Content-Type': 'application/json',
        }

    def convert_timestamp_to_readable(self, ctime: int) -> str:
        """将时间戳转换为易懂的日期时间格式"""
        return datetime.fromtimestamp(ctime).strftime('%Y-%m-%d %H:%M:%S')

    def get_oid_from_bv(self, bv_id: str) -> Optional[int]:
        """获取视频的 OID (aid)"""
        api_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bv_id}"
        try:
            response = requests.get(api_url, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()
            data = response.json()
            print(data)
            if data.get('code') == 0:
                return data['data']['aid']
        except requests.RequestException as e:
            print(f"获取 OID 时出错: {e}")
        return None

    def get_comments(self, oid: int, page: int = 1, ps: int = 20) -> Dict:
        """获取视频的评论数据"""
        url = "https://api.bilibili.com/x/v2/reply/main"
        params = {'type': 1, 'oid': oid, 'next': page, 'ps': ps}
        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {})
        except requests.RequestException as e:
            print(f"获取评论数据时出错: {e}")
        return {}

    def get_replies(self, reply_id: int, oid: int) -> List[Dict]:
        """获取评论的回复"""
        url = "https://api.bilibili.com/x/v2/reply/reply"
        params = {'oid': oid, 'type': 1, 'rpid': reply_id}
        try:
            response = requests.get(url, headers=self.headers, cookies=self.cookies, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get('data', {}).get('replies', [])
        except requests.RequestException as e:
            print(f"获取回复数据时出错: {e}")
        return []

    def _extract_comment_data(self, comment: Dict, comment_type: str) -> Dict:
        """提取单条评论的核心信息"""
        return {
            'name': comment['member']['uname'],
            'sex': comment['member'].get('sex', 'unknown'),
            'content': comment['content']['message'],
            'like': comment['like'],
            'ctime': comment['ctime'],
            'readable_time': self.convert_timestamp_to_readable(comment['ctime']),
            'type': comment_type
        }

    def _extract_replies(self, replies: List[Dict]) -> List[Dict]:
        """提取评论中的回复"""
        return [
            self._extract_comment_data(reply, comment_type='reply') for reply in replies
        ]

    def format_comments(self, bv_id: str, data: Dict) -> List[Dict]:
        """整理评论和回复数据并排序"""
        comments = []

        # 处理置顶评论
        if 'top_replies' in data:
            top_replies = data['top_replies']
            for top_reply in top_replies:
                comments.append(self._extract_comment_data(top_reply, comment_type='top'))

                # 获取置顶评论的回复
                if 'replies' in top_reply:
                    comments.extend(self._extract_replies(top_reply['replies']))

        # 处理普通评论
        for comment in data.get('replies', []):
            # 提取普通评论
            comments.append(self._extract_comment_data(comment, comment_type='normal'))
            
            # 获取并添加普通评论的回复
            if comment.get('replies'):
                comments.extend(self._extract_replies(comment['replies']))

        # 按时间排序
        return sorted(comments, key=lambda x: x['ctime'])

    def get_multiple_videos_comments(self, bv_ids: Union[List[str], str], total_pages: int = 1) -> Dict[str, List[Dict]]:
        """获取多个视频的评论并返回JSON"""
        result = {}

        if isinstance(bv_ids, str):
            bv_ids = [bv_ids]

        for bv_id in bv_ids:
            print(f"\n正在获取视频 {bv_id} 的评论...")
            oid = self.get_oid_from_bv(bv_id)
            if oid:
                print(f"视频 OID: {oid}")
                comments_data = []
                for page in range(1, total_pages + 1):
                    print(f"获取第 {page} 页评论...")
                    data = self.get_comments(oid, page)
                    if data:
                        comments = self.format_comments(bv_id, data)
                        comments_data.extend(comments)
                    else:
                        print(f"第 {page} 页没有评论数据或请求失败")
                result[bv_id] = comments_data
            else:
                print(f"无法获取视频 {bv_id} 的 OID")

        return result

# Example usage
if __name__ == "__main__":
    video_dict = {"如何一scoop": "BV1pKUkYSEjQ", "从go入手编写机器人后端（二）": "BV1AX4y1Z7Zt"}

    scraper = BilibiliCommentScraper()
    all_comments = scraper.get_multiple_videos_comments(video_dict, total_pages=1)

    # Output the result as JSON
    print(json.dumps(all_comments, ensure_ascii=False, indent=2))
