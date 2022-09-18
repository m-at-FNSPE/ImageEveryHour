import datetime
import json
import random
import urllib.request as request
import html
from functools import wraps

# API keys dictionary names
google_api_key = "google_API_key"
google_cx_key = "google_cx_key"
import cv2


test_image_1_url = "https://images.squarespace-cdn.com/content/v1/560c3567e4b03e0837f47270/1493669481606-9EGYMM9PVBLNNTFAZUJ9/IMG_3541.JPG?format=1500w"
test_image_2_url = "http://static1.squarespace.com/static/597e7c7d893fc0db64795f0d/6162e23b8ad294334b6994c0/62d0bc41f71f7410e8559e0d/1657846856920/IMG_3541.JPG?format=1500w"

temp_file_name = "temp.jpg"
face_detection_cascade_filename = "haarcascade_frontalface_default.xml"


def api_keys():
    if not hasattr(api_keys, "dictionary"):
        try:
            with open("env.json", "r") as file:
                json_file = file.read()
            api_keys.dictionary = json.loads(json_file)
        except FileNotFoundError:
            with open("env.json", "w") as file:
                x = {
                    google_api_key: "YOUR_GOOGLE_API_KEY_HERE",
                    google_cx_key: "YOUR_GOOGLE_CUSTOM_SEARCH_ENGINE_HERE"

                }
                json.dump(x, file, indent=2)
                print("File env.json not found, made one, insert your API keys.")
            exit()
    return api_keys.dictionary


def log(x):
    if not hasattr(log, "times_called_this_run"):
        log.times_called_this_run = 0

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            with open("log.txt", "a") as f:
                # Assumption that the script is run with cron, otherwise we have to implement reset of this variable
                if log.times_called_this_run == 0:
                    f.write("\n" + datetime.datetime.now().strftime("%m/%d/%Y, %H:%M") + "\n")
                f.write("Being written to from " + func.__name__ + " function\n")
                f.write(x + "\n")
                f.write("Calling the function with: " + str(args) + "\n")
                log.times_called_this_run += 1
            return result
        return wrapper
    return decorator


def get_url_for_google_search(query: str, offset: int = 0):
    url_start = "https://customsearch.googleapis.com/customsearch/v1?"
    key = "key=" + str(api_keys()[google_api_key])
    cx = "cx=" + str(api_keys()[google_cx_key])
    q = "q=" + query
    start = "start=" + str(offset)

    return url_start + key + "&" + cx + "&" + q + "&" + start


@log("Searching this query: ")
def urls_of_images_from_google_cx(query: str):
    result = []
    response = request.urlopen(query).read()
    x = json.loads(response)["items"]
    for item in x:
        try:  # sometimes the query doesn't contain the correct path
            result.append(item["pagemap"]["cse_image"][0]["src"])
        except KeyError:
            pass
    return result


def get_url_of_images(query, offset):
    return urls_of_images_from_google_cx(get_url_for_google_search(query, offset))


@log("Retrieving image from")
def download_an_image(url):  # TODO might need to handle different file types? but should be fine to keep as is
    request.urlretrieve(url, temp_file_name)


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


def download_face_detection_cascade():
    # bellow is not a permalink, might stop working (is probably fine though)
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    request.urlretrieve(url, face_detection_cascade_filename)


def random_word_from_queries_list():
    # We assume that the list is short enough
    with open("QueriesList", "r") as f:
        x = f.read()
    x = x.splitlines()
    return parse_query(x[random.randint(0, len(x) - 1)])


def how_many_faces_in_image(image_path):  # TODO modify this to detect other things (animals for example) too
    face_cascade = cv2.CascadeClassifier(face_detection_cascade_filename)
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    return len(faces)


def get_images_with_faces_from_query(query: str, offset: int = 0):
    q = []
    while len(q) == 0:
        images = get_url_of_images(query, offset)
        for i in images:
            download_an_image(i)
            if how_many_faces_in_image(temp_file_name) > 0:
                q.append(i)
        offset += 10
    return q





if __name__ == '__main__':
    download_face_detection_cascade()
    results = get_images_with_faces_from_query(random_word_from_queries_list())
    for face in results:
        print(face)




