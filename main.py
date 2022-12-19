# Discord Magnet Torrent Version 1.0
import base64
from discord_webhook import DiscordWebhook
import requests
import sys

class DiscordMagnetTorrent:
    def __init__(self, password):
        self.password = password
    
    def encode(self, file_data:bytes):
        file_data = self.encrypt(base64.b85encode(file_data).decode())
        chunk_size = 8000000
        chunked_list = []
        for i in range(0, len(file_data), chunk_size):
            chunked_list.append(file_data[i:i+chunk_size])
        return chunked_list

    def upload(self, url:str, file_data:bytes):
        print('Encoding & Encrypting...')
        chunks = self.encode(file_data)
        print('Now uploading...')
        for x in range(len(chunks)):
            webhook = DiscordWebhook(url=url, username="Magnet", rate_limit_retry=True)
            webhook.add_file(file=chunks[x], filename='upload_'+str(x)+'.bin')
            response = webhook.execute()
            print('Upload',x,response)

    def download(self, urls:list, filename:str):
        assembled = ''
        for u in urls:
            try:
                print('Downloading', u)
                if u != '':
                    assembled += requests.get(u).text
            except Exception as ex:
                print(ex)
        with open(filename, 'wb+') as f:
            f.write(base64.b85decode(self.decrypt(assembled)))

    def encrypt(self, msg):
        encryped = []
        for i, c in enumerate(msg):
            key_c = ord(self.password[i % len(self.password)])
            msg_c = ord(c)
            encryped.append(chr((msg_c + key_c) % 127))
        return ''.join(encryped)

    def decrypt(self, encryped):
        msg = []
        for i, c in enumerate(encryped):
            key_c = ord(self.password[i % len(self.password)])
            enc_c = ord(c)
            msg.append(chr((enc_c - key_c) % 127))
        return ''.join(msg)

if __name__ == '__main__':
    if len(sys.argv) > 4:
        magnet = DiscordMagnetTorrent(sys.argv[1])
        upload_or_download = sys.argv[2].__contains__("upload")
        if upload_or_download:
            url = sys.argv[3]
            with open(sys.argv[4], 'rb') as f:
                magnet.upload(url, f.read())
        else:
            links = open(sys.argv[3], 'r').read().replace('\n\n', '').split('\n')
            magnet.download(links, sys.argv[4])
        print('Done!')
    else:
        print('Please pass a few of the following arguments: password, (upload, download), (webhook_url, torrent_file), filename')
        print('Example upload: main.py password123 upload https://discord.com/api/webhooks/*/* my_upload.txt')
        print('Example download: main.py password123 download links.txt downloaded.txt')
        print('An example of what links.txt looks like is:')
        print()
        print('https://cdn.discordapp.com/attachments/*/*/upload_0.bin')
        print('https://cdn.discordapp.com/attachments/*/*/upload_1.bin')
        print()