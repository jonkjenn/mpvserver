import mpv
import server
import queue
from time import sleep
import json


def parse_data(data,player):
    d = json.loads(data)
    if isinstance(d,list):
        if len(d)>0:
            if d[0] == "mpv" and len(d)>1:
                if d[1] == "play":
                    for v in d[2]:
                        player.playlist_append(v)
                    player.playlist_pos = 0
                    print(player.video_format())
                    player.wait_for_playback()

class controller:
    def __init__(self):

        self.outq = queue.Queue()
        self.player = mpv.MPV(ytdl=True, input_default_bindings=True, input_vo_keyboard=True)
        self.player["ytdl-format"] = "bestvideo[height<=?720]+bestaudio/best"
        self.server = server.server(self.outq)

        self.loop()

    def loop(self):
        while True:
            if not self.server.inq.empty():
                try:
                    data = self.server.inq.get(timeout=1)
                    parse_data(data,self.player)
                except queue.Empty:
                    pass
            sleep(0.1)


            
if __name__=="__main__":
    c = controller()


    #@self.player.proprety_observer('time-pos')
    #def time_observer(_name,value):
