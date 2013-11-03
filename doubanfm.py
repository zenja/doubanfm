import requests
import subprocess
import threading
from ConfigParser import SafeConfigParser

class LoginException(Exception):
    pass

class DoubanFM:
    DOUBAN_URL = 'http://www.douban.com'
    APP_NAME = 'radio_desktop_win'
    APP_VERSION = 100
    DEFAULT_CHANNEL = 0

    def __init__(self):
        self.isloggedin = False
        self.playlist = []
        self.current_song = None
        self.current_channel = self.DEFAULT_CHANNEL
        self.config_parser = SafeConfigParser()
        self.config_parser.read('doubanfm.conf')
        try:
            username = config_parser.get('user', 'username')
            password = config_parser.get('user', 'password')
            self.login(username, password)
        except:
            pass

    def login(self, username, password):
        url = self.DOUBAN_URL + '/j/app/login'
        payload = {
                'email' : username,
                'password' : password,
                'app_name' : self.APP_NAME,
                'version' : self.APP_VERSION,
                }
        r = requests.post(url, data = payload)
        self.isloggedin = True
        if r.status_code == 200 and r.json()['r'] == 0:
            result_json = r.json()
            self.user_id = result_json['user_id']
            self.token = result_json['token']
            self.expire = result_json['expire']
            self.user_name = result_json['user_name']
            self.email = result_json['email']
        else:
            raise LoginException

    def get_channels(self):
        url = self.DOUBAN_URL + '/j/app/radio/channels'
        r = requests.get(url)
        return r.json()

    def change_current_channel(self, channel_id):
        self.current_channel = channel_id
        self.playlist[:] = []

    def _get_songs(self, channel_id):
        url = self.DOUBAN_URL + '/j/app/radio/people'
        payload = {
                'app_name' : self.APP_NAME,
                'version' : self.APP_VERSION,
                'sid' : '',
                'type' : 'n',
                'channel' : channel_id}
        if self.isloggedin == True:
            payload['user_id'] = self.user_id
            payload['expire'] = self.expire
            payload['token'] = self.token
        return requests.get(url, params = payload).json()

    def get_next_song(self):
        if not self.playlist:
            self.playlist = self._get_songs(self.current_channel)['song']
        self.current_song = self.playlist[-1]
        return self.playlist.pop()

    def get_current_song(self):
        return self.current_song;

class MusicPlayer:
    def __init__(self, doubanfm):
        self.doubanfm = doubanfm
        self.command = doubanfm.config_parser.get('player', 'mplayer')
        self.player_process = None
        self.volume = 100

    def play_next_song(self):
        self.stop()
        cmd = [self.command, '-slave', '-quiet', self.doubanfm.get_next_song()['url']]
        self.player_process = subprocess.Popen(cmd, stdout = subprocess.PIPE, stdin = subprocess.PIPE)
        self.change_volume(self.volume)
        # start monitoring thread
        self.monitor_thread = threading.Thread(target = self.monitor_thread_run)
        self.monitor_thread.start()

    def monitor_thread_run(self):
        # wait for the mplayer process to finish
        self.player_process.communicate(input=self.player_process.stdin)
        # notify the player to play the next song
        # if the previous song finished without interruption
        if self.player_process.returncode == 0:
            self.play_next_song()

    def stop(self):
        try:
            self.player_process.terminate()
        except:
            pass

    def change_volume(self, volume):
        self.volume = volume
        self.player_process.stdin.write("volume {} 1\n".format(volume))

    def get_current_song(self):
        return self.doubanfm.get_current_song()
