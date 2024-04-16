import lib.apiyt as apyt

class Link:
    def __init__(self,mode=None):
       self.mode = mode

    def get_link_search(self,keyword,mode):
        arr_videos=[]
        videos= apyt.get_search(f'{keyword}',mode=mode)
        for video in videos:
            arr_videos.append(f"https://www.youtube.com/watch?v={video['videoId']}")
        return self.reverse_array(arr_videos)
    
    def reverse_array(self,arr):
        start = 0
        end = len(arr) - 1
        while start < end:
            arr[start], arr[end] = arr[end], arr[start]
            start += 1
            end -= 1

        return arr



            
