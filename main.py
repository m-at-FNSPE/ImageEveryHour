import json
import random
import urllib.request as request
import html


test_image_1_url = "https://images.squarespace-cdn.com/content/v1/560c3567e4b03e0837f47270/1493669481606-9EGYMM9PVBLNNTFAZUJ9/IMG_3541.JPG?format=1500w"
test_image_2_url = "http://static1.squarespace.com/static/597e7c7d893fc0db64795f0d/6162e23b8ad294334b6994c0/62d0bc41f71f7410e8559e0d/1657846856920/IMG_3541.JPG?format=1500w"


def api_keys():
    with open("env.json", "r") as file:
        json_file = file.read()
    return json.loads(json_file)


def get_url_for_google_search(query: str, offset: int = 0):
    url_start = "https://customsearch.googleapis.com/customsearch/v1?"
    key = "key=" + str(api_keys()["google_API_key"])
    cx = "cx=" + str(api_keys()["cx"])
    q = "q=" + query
    start = "offset=" + str(offset)

    return url_start + key + "&" + cx + "&" + q + "&" + start


def urls_of_images_from_query(query):
    # print(get_url_for_google_search(query))
    result = []
    response = request.urlopen(get_url_for_google_search(query)).read()
    x = json.loads(response)["items"]
    for item in x:
        result.append(item["pagemap"]["cse_image"][0]["src"])
    return result


def parse_query(word: str):
    result = ""
    word.encode()
    for i in word:
        result = result + str(replace_letter(i))
    return result


def replace_letter(i):
    if i == "!":
        i = str(random.randint(0, 9))
    return html.escape(i)


def random_word_from_queries_list():
    # We assume that the list is short enough
    with open("QueriesList", "r") as f:
        x = f.read()
    x = x.splitlines()
    return x[random.randint(0, len(x) - 1)]


def random_query():
    return parse_query(random_word_from_queries_list())


if __name__ == '__main__':
    for i in range(20):
        print(random_query())
