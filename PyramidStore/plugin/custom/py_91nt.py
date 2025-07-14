# coding: utf-8
# 文件: py_spider/PyramidStore/plugin/custom/py_91nt.py

from base.spider import Spider as BaseSpider
import requests
from bs4 import BeautifulSoup
import json

# 这是必需的库，如果您的环境没有，请安装
# pip install requests beautifulsoup4

class Spider(BaseSpider):
    # 爬虫的显示名称
    def getName(self):
        return "91NT"

    # 爬虫的唯一标识
    def getKey(self):
        return "91nt"

    # 网站域名
    def getSiteUrl(self):
        return "https://91nt.com"

    # 初始化方法，可以在这里设置请求头等
    def init(self, extend=""):
        super().init(extend)
        self.s = requests.Session()
        self.s.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36'
        })
        print(f"爬虫 [{self.getName()}] 初始化完成...")

    # 获取分类数据
    # 这个方法会在首页上显示分类
    def homeContent(self, filter):
        try:
            # 您需要访 91nt.com，查看其分类，然后在这里手动创建
            # 'type_id' 的值是分类页面的URL路径
            result = {
                'class': [
                    {'type_name': '精选G片', 'type_id': '/videos/all/watchings'},
                    {'type_name': '男同黑料', 'type_id': '/posts/category/all'},
                    {'type_name': '热搜词', 'type_id': '/hot/1'},
                    {'type_name': '鲜肉薄肌', 'type_id': '/videos/category/xrbj'},
                    {'type_name': '无套内射', 'type_id': '/videos/category/wtns'},
                    {'type_name': '制服诱惑', 'type_id': '/videos/category/zfyh'},
                    {'type_name': '耽美天菜', 'type_id': '/videos/category/dmfj'},
                    {'type_name': '肌肉猛男', 'type_id': '/videos/category/jrmn'},
                    {'type_name': '日韩GV', 'type_id': '/videos/category/rhgv'},
                    {'type_name': '欧美巨屌', 'type_id': '/videos/category/omjd'},
                    {'type_name': '多人群交', 'type_id': '/videos/category/drqp'},
                    {'type_name': '口交颜射', 'type_id': '/videos/category/kjys'},
                    {'type_name': '调教SM', 'type_id': '/videos/category/tjsm'}
                ]
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            print(f"获取首页分类失败: {e}")
            return "{}"

    # 获取首页最近更新的视频内容
    # 通常是首页上直接显示的那些视频
    def homeVideoContent(self):
        try:
            url = self.getSiteUrl()
            res = self.s.get(url, timeout=10)
            res.raise_for_status() # 如果请求失败则引发异常
            
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # --- 核心逻辑开始 ---
            # 查找“最近更新”板块
            recent_updates_section = None
            for heading in soup.find_all('h3'):
                if '最近更新' in heading.text:
                    recent_updates_section = heading.find_parent()
                    break

            videos = []
            if recent_updates_section:
                video_items = recent_updates_section.find_next_sibling('div').find_all('div', recursive=False)

                for item in video_items:
                    a_tag = item.find('a')
                    if not a_tag:
                        continue
                    
                    img_tag = a_tag.find('img')
                    
                    vod_id = a_tag['href'] 
                    vod_name = img_tag['alt'] if img_tag else a_tag.text.strip()
                    vod_pic = img_tag['src'] if img_tag else ''
                    
                    duration_tag = a_tag.find('div', class_='absolute')
                    vod_remarks = duration_tag.text.strip() if duration_tag else ''
                    
                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": vod_name,
                        "vod_pic": vod_pic,
                        "vod_remarks": vod_remarks
                    })
            # --- 核心逻辑结束 ---
            
            return json.dumps({'list': videos}, ensure_ascii=False)
        except Exception as e:
            print(f"获取首页视频失败: {e}")
            return "{}"

    # 获取分类页的视频列表
    # 当用户点击提取到网页实际的分类时调用
    def categoryContent(self, tid, pg, filter, extend):
        try:
            # tid 就是 homeContent 中定义的 'type_id'
            url = self.getSiteUrl() + tid + f"?page={pg}"
            res = self.s.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # 这里的逻辑和 homeVideoContent 非常相似，您也需要根据实际页面修改
            video_list_container = soup.find('div', class_='grid-flow-row')
            videos = []
            if video_list_container:
                video_items = video_list_container.find_all('div', recursive=False)
                for item in video_items:
                    a_tag = item.find('a')
                    if not a_tag:
                        continue
                    
                    img_tag = a_tag.find('img')
                    
                    vod_id = a_tag['href']
                    vod_name = img_tag['alt'] if img_tag else a_tag.text.strip()
                    vod_pic = img_tag['src'] if img_tag else ''
                    
                    duration_tag = a_tag.find('div', class_='absolute')
                    vod_remarks = duration_tag.text.strip() if duration_tag else ''

                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": vod_name,
                        "vod_pic": vod_pic,
                        "vod_remarks": vod_remarks
                    })
            
            # 框架需要知道总页数、当前页数、每页数量、总数量等信息
            pagecount = 1
            pagination_info = soup.find('div', class_='text-sm')
            if pagination_info and '/' in pagination_info.text:
                pagecount = int(pagination_info.text.split('/')[1].strip())

            result = {
                'page': int(pg),
                'pagecount': pagecount,
                'limit': len(videos),
                'total': pagecount * len(videos), # Estimate total
                'list': videos
            }
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            print(f"获取分类页 '{tid}' 失败: {e}")
            return "{}"

    # 获取视频详情
    # 当用户点击一个具体的视频时调用
    def detailContent(self, ids):
        try:
            # ids 是一个列表，但通常我们只处理第一个
            url = self.getSiteUrl() + ids[0]
            res = self.s.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # --- 核心逻辑开始 ---
            title_tag = soup.find('h1')
            vod_name = title_tag.text.strip() if title_tag else ''

            # 尝试从 video 标签的 poster 获取封面
            video_tag = soup.find('video')
            vod_pic = video_tag['poster'] if video_tag and 'poster' in video_tag.attrs else ''

            # 获取类别
            type_name_tags = soup.select('div.flex.flex-wrap a')
            type_name = '/'.join([a.text.strip() for a in type_name_tags]) if type_name_tags else ''

            # 获取上传者信息
            author_tag = soup.select_one('a[href*="/publicvideo/"]')
            vod_actor = author_tag.text.strip() if author_tag else 'N/A'
            
            # 获取简介
            description_tag = soup.select_one('div.mt-4.text-sm.text-gray-400')
            vod_content = description_tag.text.strip() if description_tag else ''

            # 播放列表, 该网站是直接播放，只有一个播放地址
            play_url = ids[0] # 使用详情页的路径作为播放标识
            
            vod = {
                "vod_id": ids[0],
                "vod_name": vod_name,
                "vod_pic": vod_pic,
                "type_name": type_name, 
                "vod_year": "", # 年份
                "vod_area": "", # 地区
                "vod_remarks": "高清", # 备注
                "vod_actor": vod_actor,
                "vod_director": "", # 导演信息缺失
                "vod_content": vod_content,
                "vod_play_from": self.getName(), # 播放源名称
                "vod_play_url": f"播放${play_url}" # 格式: "集数$播放链接"
            }
            # --- 核心逻辑结束 ---
            
            return json.dumps({'list': [vod]}, ensure_ascii=False)
        except Exception as e:
            print(f"获取详情页 '{ids[0]}' 失败: {e}")
            return "{}"

    # 获取播放地址
    # 这个方法在最终播放前调用，有些网站的播放地址是二次解析的
    def playerContent(self, flag, id, vipFlags):
        # flag: 播放源, '91NT'
        # id: 播放链接, 实际上是详情页的路径
        # 如果 detailContent 中获取的播放链接已经是最终地址（如 .m3u8, .mp4），可以直接返回
        try:
            url = self.getSiteUrl() + id
            res = self.s.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')

            video_url = ''
            video_tag = soup.find('video')
            if video_tag:
                source_tag = video_tag.find('source')
                if source_tag and 'src' in source_tag.attrs:
                    video_url = source_tag['src']
                elif 'src' in video_tag.attrs:
                    video_url = video_tag['src']

            return json.dumps({
                'parse': 0, # 0=直接播放, 1=需要网页嗅探/解析
                'playUrl': '', # 如果parse为1，这里是嗅探用的网页地址
                'url': video_url, # 最终的播放地址
                'header': '' # 如果需要特定请求头，在这里设置
            })
        except Exception as e:
            print(f"解析播放地址 '{id}' 失败: {e}")
            return "{}"

    # 搜索功能
    def searchContent(self, key, quick):
        # quick 参数在这里可能用不到
        try:
            url = f"{self.getSiteUrl()}/videos/search/{key}" 
            res = self.s.get(url, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, 'html.parser')
            
            videos = []
            video_list_container = soup.find('div', class_='grid-flow-row')
            if video_list_container:
                video_items = video_list_container.find_all('div', recursive=False)
                for item in video_items:
                    a_tag = item.find('a')
                    if not a_tag:
                        continue
                    
                    img_tag = a_tag.find('img')
                    
                    vod_id = a_tag['href']
                    vod_name = img_tag['alt'] if img_tag else a_tag.text.strip()
                    vod_pic = img_tag['src'] if img_tag else ''
                    
                    duration_tag = a_tag.find('div', class_='absolute')
                    vod_remarks = duration_tag.text.strip() if duration_tag else ''

                    videos.append({
                        "vod_id": vod_id,
                        "vod_name": vod_name,
                        "vod_pic": vod_pic,
                        "vod_remarks": vod_remarks
                    })
                
            return json.dumps({'list': videos}, ensure_ascii=False)
        except Exception as e:
            print(f"搜索 '{key}' 失败: {e}")
            return "{}"