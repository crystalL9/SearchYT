from search_youtube import DetailCrawler

tool = DetailCrawler()
url='https://www.youtube.com/watch?v=hxNM-6k1-W4'
proxy = {
                "http": "http://192.168.143.101:4016",
                "https": "http://192.168.143.101:4016"
        }
print(tool.get_full_video_information(video_url=url,proxies=proxy))