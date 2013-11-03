from flask import Flask
from doubanfm import DoubanFM, MusicPlayer

app = Flask(__name__)
doubanfm = DoubanFM()
player = MusicPlayer(doubanfm)

@app.route('/')
def index():
    return "Hello World!"

@app.route('/api/v1/next')
def next_song():
    player.play_next_song()
    current_song = player.get_current_song()
    if current_song:
        return u'Playing now: {0} by {1}'.format(unicode(current_song['title']), unicode(current_song['artist']))
    else:
        return 'There is no current song.'

@app.route('/api/v1/stop')
def stop():
    player.stop()
    return 'Player should be stopped now'

@app.route('/api/v1/change_volume/<int:volume>')
def change_volume(volume):
    if 1 <= volume <= 100:
        player.change_volume(volume)
        return "Current volume: {0}".format(player.volume)
    else:
        return "Volume should between 1 and 100 (inclusive)"

@app.route('/api/v1/info')
def info():
    if doubanfm.current_song:
        return u'Current song: {0} by {1}'.format(unicode(doubanfm.current_song['title']), unicode(doubanfm.current_song['artist']))
    else:
        return 'There is no current song now.'

@app.route('/api/v1/channels')
def channels():
    return str(doubanfm.get_channels())

@app.route('/api/v1/change_channel/<int:channel_id>')
def change_channel(channel_id):
    doubanfm.change_current_channel(channel_id)
    next_song()
    return 'current channel: {0}'.format(doubanfm.current_channel)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
