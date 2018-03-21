# coding: utf-8
import requests
import os
import math
import configparser # for Python3
import urllib
import re
import datetime
# 自作モジュール
import bing_util

def get_headers(api_key):
    return {"Ocp-Apim-Subscription-Key" : api_key}

def get_params(search_term, num_imgs_per_transaction, offset):
    return urllib.parse.urlencode({
        "q": search_term,
        # ライセンスを無視して集める
        "license": "All",
        "imageType": "photo",
        "count":num_imgs_per_transaction,
        "offset": offset * num_imgs_per_transaction,
        "mkt":"ja-JP"})

def get_search_results(search_url, headers, params):
    response = requests.get(search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()
    return search_results

def save_urls(results, filepath):    
    with open(filepath, mode='a') as f:
        for values in results:
            if values['encodingFormat'] == 'jpeg':
                print(values['contentUrl'], file=f)

def get_filename(path, fn, ext):
    return os.path.join(path, '%s.%s' % (fn, ext))

# 得られたURLを記録するファイルを作製する関数
def gen_url_save_file(search_term, url_dir_path, total_count):
    # extention(拡張子)
    ext = 'txt'
    fn = bing_util.search_term2file_name(search_term)
    filename = get_filename(url_dir_path, fn, ext)
    dt = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    if os.path.isfile(filename):
        fn = '%s_%s' % (fn, dt)
        filename = get_filename(url_dir_path, fn, ext)
    with open(filename, mode='w') as f:
        print("date=%s, search_term=%s, totalEstimatedMatches=%d" % (dt, search_term, total_count), file=f)
    return filename


if __name__ == '__main__':
    # auth.ini読み込み
    config = configparser.ConfigParser()
    config.read('authentication.ini')
    bing_api_key = config['auth']['bing_api_key']

    # URL取得リストを保存するディレクトリを指定．なければ作る
    save_dir_path = './bing'
    bing_util.make_dir(save_dir_path)
    url_dir_path = os.path.join(save_dir_path, 'url')
    bing_util.make_dir(url_dir_path)

    # ほしい画像枚数．取得するURLリストの上限．
    num_imgs_required = 1000
    # Bingリクエスト1回あたりに取得する画像URL．
    # default 30, Max 150 images
    num_imgs_per_transaction = 150
    # 検索キーワード入力
    search_term = "大空直美"


    search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"

    headers = get_headers(bing_api_key)
    params = get_params(search_term, num_imgs_per_transaction, 0)

    first_search_results = get_search_results(search_url, headers, params)
    total_count = first_search_results["totalEstimatedMatches"]
    print("totalEstimatedMatches=%d" % total_count)

    filepath=gen_url_save_file(search_term, url_dir_path, total_count)

    print ("len=%d" % (len(first_search_results["value"])))
    save_urls(first_search_results["value"], filepath)

    if num_imgs_required > total_count :
        num_imgs_required = total_count

    offset_count = math.ceil(num_imgs_required / num_imgs_per_transaction)
    print('offset_count=%d' % offset_count)
    for offset in range(1, offset_count):
        params = get_params(search_term, num_imgs_per_transaction, offset)
        search_results = get_search_results(search_url, headers, params)

        print ("len=%d" % len(search_results["value"]))
        save_urls(search_results["value"], filepath)