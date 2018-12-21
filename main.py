# -*- coding: utf-8 -*-
import json
import multiprocessing as mp
import urllib.request
from threading import Thread
from urllib import parse

from bs4 import BeautifulSoup
from flask import Flask, request, make_response
from slackclient import SlackClient

from keyword_maker import KeywordMaker

app = Flask(__name__)

slack_token = "xoxb-506062083639-508075067825-40MNlihpFEwKYVp01V2i4pxA"
slack_client_id = "506062083639.509730436711"
slack_client_secret = "139e3ea0d6e685fad03e5a0cebcbd0ca"
slack_verification = "PP3eQd4eRfAKR3GPcN0DFmd8"
sc = SlackClient(slack_token)


def __korean_to_unicode(str):
    parse_url = parse.urlparse("https://www.diningcode.com/list.php?query={0}".format(str))
    query = parse.parse_qs(parse_url.query)
    return parse.urlencode(query, doseq=True).split('=')[1]


def __crawl_get_request_one_url_return_item(query):
    url = "https://www.diningcode.com/list.php?query={0}".format(query)
    req = urllib.request.Request(url)
    sourcecode = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(sourcecode, "html.parser")

    list_link = []
    list_ranking = []

    title = []
    category = []
    ratings = []
    address = []
    phoneNum = []
    menuList = []

    keywords = []

    for links in soup.find_all("li")[5:]:
        list_link.append("https://www.diningcode.com" + links.find("a")["href"])
        list_ranking.append(links.find("span", class_="btxt").get_text().strip())

    for i in range(0, len(list_link)):
        url = list_link[i]
        req = urllib.request.Request(url)
        sourcecode = urllib.request.urlopen(url).read()
        soup = BeautifulSoup(sourcecode, "html.parser")
        for elem in soup.find_all("div", class_="div-cont"):
            title.append(elem.find("div", class_="tit-point").get_text().strip())
            category.append(elem.find("div", class_="btxt").get_text().strip()[6:])
            ratings.append(elem.find("p", class_="grade").get_text().strip()[0:3])
            address.append(elem.find("li", class_="locat").get_text().strip())
            phoneNum.append(elem.find("li", class_="tel").get_text().strip())
            if not elem.find_all("div", class_="menu-info short"):
                menuList.append("정보없음")
            else:
                for j in elem.find_all("div", class_="menu-info short"):
                    menuList.append(
                        j.get_text().strip().replace('\n', '').replace('\t', '-').replace('더보기', '').replace('원',
                                                                                                             '원\n')[4:])
    for i in range(0, len(list_ranking)):
        # keywords.append(list_ranking[i] + " " + list_link[i])
        keywords.append(list_ranking[i])
        keywords.append("카테고리: {0}".format(category[i]))
        keywords.append("평점: {0}".format(ratings[i]))
        keywords.append("주소: {0}".format(address[i]))
        keywords.append("전화번호: {0}".format(phoneNum[i]))
        keywords.append("주요메뉴: \n{0}".format(menuList[i]))

    return keywords


# 크롤링 함수 구현하기
def processing_function(text):
    text = text[13:]
    keywords = []
    query_list = []

    maker = KeywordMaker()
    result_tuple = maker.get_search_tuple(text)
    location_list = result_tuple[0]
    category_list = result_tuple[1]
    franchise_list = result_tuple[2]

    # 1 장소입력이 없을때 -> 서울기준
    if len(location_list) == 0:
        location_list.append("서울")

    # 2 카테고리가 없을때 -> 장소  # 3 카테고리가 많을때 -> (장소 + 카테고리)
    for category in category_list:
        tmpUrl = __korean_to_unicode(location_list[0]) + "%20" + __korean_to_unicode(category) + "%20"
        query_list.append(tmpUrl)

    # 4 프렌차이즈가 있을 때
    # if len(franchise_list)>0:

    for query in query_list:
        list__ = __crawl_get_request_one_url_return_item(query)
        keywords += list__



    return u'\n'.join(keywords)


# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    # print(slack_event["event"])
    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]

        keywords = processing_function(text)

        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text=keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })
    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response

    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"


def processing_event(queue):
    while True:
        # 큐가 비어있지 않은 경우 로직 실행
        if not queue.empty():
            slack_event = queue.get()

            # Your Processing Code Block gose to here
            channel = slack_event["event"]["channel"]
            text = slack_event["event"]["text"]

            # 챗봇 크롤링 프로세스 로직 함수
            keywords = processing_function(text)

            # 아래에 슬랙 클라이언트 api를 호출하세요
            sc.api_call(
                "chat.postMessage",
                channel=channel,
                text=keywords
            )


if __name__ == '__main__':
    event_queue = mp.Queue()
    p = Thread(target=processing_event, args=(event_queue,))
    p.start()

    print("start!!")
    app.run('127.0.0.1', port=5000)
