import os
from flask import Flask, request, Response
import requests
from werkzeug.contrib.cache import MemcachedCache
cache = MemcachedCache(['127.0.0.1:11211'])

app = Flask(__name__)

WONDER_TRACKLIST_ID = 65
WHITELABEL_TRACKLIST_ID = 68


@app.route('/whitelabel', methods=['GET'])
def whitelabel():
    return common_fetcher(request, WHITELABEL_TRACKLIST_ID)


def wonder():
    return common_fetcher(request, WONDER_TRACKLIST_ID)

def common_fetcher(request, list_id):
    callback = request.args.get('callback', False)

    response_text = fetch_boxset_list(list_id)
    if callback:
        response_text = str(callback) + '(' + response_text + ')'

    return Response(response_text, 200, mimetype = 'application/javascript')


def fetch_boxset_list(list_id):
    cache_key = 'list-{}'.format(list_id)
    rv = cache.get(cache_key)
    if rv is None:
        r = requests.get('http://boxset.io/api/v0.1/track_list/?tracklist_id={}&version_type=LT'.format(list_id))
        track_list_url = r.json()['objects'][0]['tracks']
        rv = requests.get('http://boxset.io/{}&{}'.format(track_list_url,'limit=99&namespaces=soundcloud,wonder,twitter&format=json'))
        cache.set(cache_key, rv.text, timeout=5 * 60)
    return rv.text

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
