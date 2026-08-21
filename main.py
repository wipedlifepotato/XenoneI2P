import requests, re,json
#https://transmission-rpc.readthedocs.io/en/v7.0.12/
#https://github.com/transmission/transmission/blob/main/docs/rpc-spec.md
#from transmission_rpc import Client
from urllib.parse import urlsplit
import transmission_rpc
class TorrentWrapper():
    def __init__(self, rpchost="127.0.0.1", rpcport=9191, rpcuser="", rpcpassword=""):
        self.rpchost = rpchost
        self.rpcport = rpcport
        self.rpcuser = rpcuser
        self.rpcpassword = rpcpassword
    def client(self): return transmission_rpc.Client(host=self.rpchost, port=self.rpcport, username=self.rpcuser, password=self.rpcpassword, path="/mytorrents/rpc/")
    def add(self, w: str, is_magnet: bool = False, http_proxy_port: int = 4444):
        if is_magnet: 
            raise ValueError("Magnet links not implemented in i2p for a while (check in last commits of i2pd or change")
            self.client().add_torrent(w)
        else:
            c = self.client()
            parsed = urlsplit(w)
            netloc = parsed.netloc
            if not netloc or parsed.scheme not in ("http", "https"): raise ValueError("This is not http and not magnet") # False # better a throw maybe
            if netloc.split('.')[-1] != 'i2p': raise ValueError("not i2p link") # better a throw maybe
            try:
             print(w)
             response = requests.get(w, proxies={"http":f"http://127.0.0.1:{http_proxy_port}"}, timeout=60)
             response.raise_for_status()
             c.add_torrent(response.content)
             return True
            except Exception as err: 
                print(f"err to add torrent!: {str(err)}")
                return False
    def get(self):
        try:
            c = self.client()
            fields = ["id", "name", "status", "rateDownload", "rateUpload", "totalSize"]
            torrents = c.get_torrents(arguments=fields)
            return torrents
        except Exception as err:
            err_message = str(err)
            match = re.search(r"\{.*\}", err_message)
            if match:
                raw_json_str = match.group(0)
                fixed_json_str = raw_json_str.replace("'", '"')
                #print(fixed_json_str)
                try:
                 parsed_data = json.loads(fixed_json_str)
                 #print(parsed_data)
                 torrents = parsed_data.get("torrents", [])
                 return torrents
                except Exception as exc:
                 print("Exception:" + str(exc))
                 return False
    pass
	# todo, ...


def main():
    t = TorrentWrapper()
    #t.add('magnet:?xt=urn:btih:c8a431d53b00314211a78b6b8388ceb8dcbb3680&dn=Tetrazole.+Explosions+stuff.+&tr=http://tracker2.postman.i2p/announce.php', is_magnet=True)
    #t.add("http://tracker2.postman.i2p/index.php?action=Download&id=55406", is_magnet=False)
    torrents = t.get()
    for torrent in torrents:
        print(torrent)
    pass

if __name__ == "__main__":
	main()
