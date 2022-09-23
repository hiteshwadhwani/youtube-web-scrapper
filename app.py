import pandas as pd
from flask import Flask, render_template, request, jsonify, url_for
from flask_cors import CORS, cross_origin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import os
import handle_S3_videos
import config
# For handling logs
import logging_file

# https://docs.python.org/3/library/urllib.parse.html
from urllib.parse import urlparse
from connect_with_sql import save_to_sql
from connect_with_mongoDB import handle_data_mongoDB

app = Flask(__name__)

# home page route
@app.route('/', methods=['GET', 'POSt'])
@cross_origin()
def home():
    logging_file.config()
    config.configure()
    logging_file.info("Some visited website")
    return render_template("home.html")

# success page route for VERSION:2 (This route will only show scrapped data from JSON file) (USED IN DEPLOYED VERSION)
@app.route('/success', methods=['POST'])
def success():
    name = request.form['content']
    number_of_videos = int(request.form['number'])
    df = pd.read_json(f"./files/{name.replace(' ','_')}.json")
    return render_template("success1.html", list_data=df.values.tolist()[:number_of_videos])

@app.route("/download/<id>")
def download(id):
    url = f"https://www.youtube.com/watch?v={id}"
    link = handle_S3_videos.handle_videos(url)
    return f"<a href={link}>Video URL</a>"

# Success page route for VERSION:1 (This route can scrape any youtubers data)(Will ony work in local system)
# @app.route('/success', methods=['POST'])
# def success():
#     if request.method == 'POST':
#         name = request.form['content']
#         number_of_videos = int(request.form['number'])
#         # sql_username = request.form['sql-username']
#         # sql_password = request.form['sql-password']
#         logging_file.info(f"user searched for {name} and he wants {number_of_videos} videos")
#         handle_S3_videos.reset_directory()
#         urls = image_URL(name, number_of_videos)
#         df = pd.DataFrame(urls)
#         df.to_json(f"./files/{name.replace(' ','_')}.json", indent=False)
#         print("length of urls ", len(urls))
#         # handle_data_mongoDB(urls, name.replace(" ", "_"))
#         # save_to_sql(sql_username, sql_password, urls, name.replace(" ", "_"))
#         return render_template("success.html", list_data=urls)


def image_URL(name_to_search, number_of_links):
    ser = Service("chromedriver.exe")
    op = webdriver.ChromeOptions()
    # op.add_argument("--headless")
    # op.add_argument("--disable-dev-shm-usage")
    # op.add_argument("--no-sandbox")
    op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(service=ser, options=op)
    url = "https://www.youtube.com/results?search_query={}"
    name = name_to_search.replace(" ", "+")
    driver.get(url.format(name))
    time.sleep(5)
    user_url = driver.find_element(By.ID, "main-link").get_attribute("href")
    driver.get(user_url + "/videos")
    time.sleep(3)

    def scroll_down():
        wait = WebDriverWait(driver, 1)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
        time.sleep(1)

    # links of youtube videos
    links = driver.find_elements(By.ID, "thumbnail")
    links1 = set()
    for i in links:
        if 'shorts' not in str(i.get_attribute("href")):
            links1.add(str(i.get_attribute("href")))
    if len(links1) < number_of_links:
        while True:
            scroll_down()
            links = driver.find_elements(By.ID, "thumbnail")
            for i in links:
                if 'shorts' not in str(i.get_attribute("href")):
                    links1.add(str(i.get_attribute("href")))

            # base condition where loop will break else it will scroll down and append links
            if len(links1) >= number_of_links:
                break

    information = []
    for link in list(links1)[0:number_of_links]:
        try:
            data = get_video_information(link, driver)
            information.append(data)
        except:
            pass
    return information


def get_video_information(url: str, driver: webdriver):
    global comment_count, likes, title, comments
    driver.get(url)

    wait = WebDriverWait(driver, 1)

    time.sleep(5)

    # This function scrolls page to the end
    def scroll_to_end():
        for item in range(10):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(1)

    scroll_to_end()
    time.sleep(5)

    # title of the video
    try:
        title = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/h1/yt-formatted-string'))).get_attribute(
            "innerText")
    except:
        pass

    # Likes of the video
    # likes = driver.find_element(By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a').text
    try:
        likes = wait.until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a'))).text
    except:
        pass

    # number of comments on the video
    # comment_count = (driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]')).text
    try:
        comment_count = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]'))).text
    except:
        pass

    # Comments on the video
    try:
        commentNew = driver.find_elements(By.XPATH, '//*[@id="body"]')
        comments = []
        for i in commentNew:
            comments.append({"name": i.find_element(By.CSS_SELECTOR, '#header-author > h3').text,
                             "comment": i.find_element(By.ID, 'comment-content').text})
    except:
        pass

    # Download video and upload in S3 Bucket and create URL


    details = {'url': url, "title": title, "likes": likes, "number_of_comments": comment_count,
               'thumbnail': f'http://img.youtube.com/vi/{urlparse(url).query[2::]}/maxresdefault.jpg',
               "S3_Bucket_URL": 'None', "comments": comments, "id": urlparse(url).query[2::]}

    return details


if __name__ == '__main__':
    app.run()
