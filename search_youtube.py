import json
import re
import time
import requests
import datetime
import json
from pytube import YouTube
class DetailCrawler:
    def __init__(self):
        pass
    def extract_post_infor(self,video_url):
        list_json=[]
        result_request= requests.get(video_url)
        result_json_1=json.loads(result_request.text.split('var ytInitialPlayerResponse = ')[-1].split(';</script>')[0])
        result_json_2=json.loads(result_request.text.split('var ytInitialData = ')[-1].split(';</script>')[0])
        data= result_json_1['videoDetails']
        print(data["viewCount"])
        data2 = result_json_1['microformat']
        avatar = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['thumbnail']['thumbnails'][0]['url']
        hashtag = []
        try:
            list_hashtag = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['superTitleLink']['runs']
            for l in list_hashtag:
                if l['text']!=' ' and l['text']!=None :
                    hashtag.append(l['text'])
        except:
            pass
        comment = 0
        try:
            comment_element = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][2]['itemSectionRenderer']['contents'][0]['commentsEntryPointHeaderRenderer']['commentCount']
            comment = int(comment_element['simpleText'])
        except:
            pass

        like=0
        try:
            like_txt=result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel']['likeButtonViewModel']['likeButtonViewModel']['toggleButtonViewModel']['toggleButtonViewModel']['defaultButtonViewModel']['buttonViewModel']['accessibilityText']
            likes = re.findall(r'\d+[\.,\d]*', like_txt)
            like = [int(num.replace('.', '').replace(',', '')) for num in likes][0]
        except:
            pass
        list_json.append(data)
        list_json.append(data2)
        list_json.append(hashtag)
        list_json.append(comment)
        list_json.append(like)
        list_json.append(avatar)
        return list_json


    def get_full_video_information(self,video_url,proxies):
        try:
            if proxies['http']=='' or proxies['http']==None:
                result_request= requests.get(video_url)
            else:
                result_request= requests.get(video_url,proxies)
            json_list=[]
            result_json_1=json.loads(result_request.text.split('var ytInitialPlayerResponse = ')[-1].split(';</script>')[0])
            result_json_2=json.loads(result_request.text.split('var ytInitialData = ')[-1].split(';</script>')[0])
            data= result_json_1['videoDetails']
            data2 = result_json_1['microformat']
            avatar = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['owner']['videoOwnerRenderer']['thumbnail']['thumbnails'][0]['url']
            hashtag = []
            try:
                list_hashtag = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['superTitleLink']['runs']
                for l in list_hashtag:
                    if l['text']!=' ' and l['text']!=None :
                        hashtag.append(l['text'])
            except:
                pass
            comment = 0
            try:
                comment_element = result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][2]['itemSectionRenderer']['contents'][0]['commentsEntryPointHeaderRenderer']['commentCount']
                comment = int(comment_element['simpleText'])
            except:
                pass

            like=0
            try:
                like_txt=result_json_2['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0]['segmentedLikeDislikeButtonViewModel']['likeButtonViewModel']['likeButtonViewModel']['toggleButtonViewModel']['toggleButtonViewModel']['defaultButtonViewModel']['buttonViewModel']['accessibilityText']
                likes = re.findall(r'\d+[\.,\d]*', like_txt)
                like = [int(num.replace('.', '').replace(',', '')) for num in likes][0]
            except:
                pass
            json_list.append(data)
            json_list.append(data2)
            json_list.append(hashtag)
            json_list.append(comment)
            json_list.append(like)
            json_list.append(avatar)

            data= eval(str(json_list[0]))
            data2= eval(str(json_list[1]))
            video_info = {}
            current_time = int(datetime.datetime.now().timestamp())
            video_info["time_crawl"] = current_time
            video_info["author"]=data["author"]
            video_info["author_link"]=data2["playerMicroformatRenderer"]["ownerProfileUrl"]
            video_info["author_id"]=data['channelId']
            video_info["link"] = video_url
            video_info["id"] = f'yt_{data["videoId"]}'
            id=data["videoId"]
            video_info["title"] = data["title"]
            video_info["source_id"]=''
            try:
                video_info["description"] = data2["playerMicroformatRenderer"]["description"]["simpleText"]
            except:
                video_info["description"]=''
            try:
                video_info["hashtag"]=json_list[2]
            except:
                video_info["hashtag"]=[]
            video_info["type"] = "youtube video"
            video_info["domain"] = "www.youtube.com"
            
            try: 
                video_info["like"] = int(json_list[4])
            except: 
                video_info["like"]= 0
            video_info["avatar"] = json_list[5]
            try:
                video_info["view"]=int(data["viewCount"])
            except:
                video_info["view"]=0
            video_info['created_time'] = int(datetime.datetime.strptime(data2["playerMicroformatRenderer"]["uploadDate"], "%Y-%m-%dT%H:%M:%S%z").timestamp())
            video_info["duration"] = int(data["lengthSeconds"])
            video_info['content']= ''
            time.sleep(2)
            try: 
                video_info["comment"] = int(json_list[3])
            except: 
                video_info["comment"]=0
            return video_info
        except Exception as e:
            print("Exception at extract_video_info_json(): ",e)
            return
    

    def extract_video_id(self, video_link):
        pattern = r"(?:watch\?v=)([a-zA-Z0-9_-]{11})"
        match = re.search(pattern, video_link)
        if match:
            return match.group(1)
        return None


    def link_to_id(self,link):
        yt = YouTube(link)
        video_id = yt.video_id
        return video_id

   