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

app = Flask(__name__)


@app.route('/', methods=['GET', 'POSt'])
@cross_origin()
def hello_world():
    logging_file.config()
    config.configure()
    logging_file.info("Some visited website")
    return render_template("home.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        name = request.form['content']
        number_of_videos = int(request.form['number'])
        sql_username = request.form['sql-username']
        sql_password = request.form['sql-password']
        download_video = request.form.get("video")
        logging_file.info(f"user searched for {name} and he wants {number_of_videos} videos")
        handle_S3_videos.reset_directory()
        urls = image_URL(name, number_of_videos, download_video)
        print("length of urls ", len(urls))
        save_to_sql(sql_username, sql_password, urls, name.replace(" ", "_"))
        # return jsonify(str(urls))

        return render_template("success.html", list_data=urls)
        # return 'hello world'


def image_URL(name_to_search, number_of_links, download_video):
    ser = Service("chromedriver.exe")
    op = webdriver.ChromeOptions()
    op.add_argument("--headless")
    op.add_argument("--disable-dev-shm-usage")
    op.add_argument("--no-sandbox")
    op.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    driver = webdriver.Chrome(service=ser, options=op)
    url = "https://www.youtube.com/results?search_query={}"
    name = name_to_search.replace(" ", "+")
    driver.get(url.format(name))
    user_url = driver.find_element(By.ID, "main-link").get_attribute("href")
    driver.get(user_url + "/videos")

    def scroll_down():
        wait = WebDriverWait(driver, 1)
        wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
        time.sleep(1)

    # links of youtube videos
    links = driver.find_elements(By.ID, "thumbnail")
    links1 = set()
    for i in links:
        if 'shorts' not in str(i.get_attribute("href")):
            links1.add(i.get_attribute("href"))
    if len(links1) < number_of_links:
        while True:
            scroll_down()
            links = driver.find_elements(By.ID, "thumbnail")
            for i in links:
                if 'shorts' not in str(i.get_attribute("href")):
                    links1.add(i.get_attribute("href"))

            # base condition where loop will break else it will scroll down and append links
            if len(links1) >= number_of_links:
                break

    information = []
    for link in list(links1)[0:number_of_links]:
        information.append(get_video_information(link, driver, download_video))
    return information


def get_video_information(url: str, driver: webdriver, download_video):
    driver.get(url)

    wait = WebDriverWait(driver, 1)

    time.sleep(5)

    # This function scrolls page to the end
    def scroll_to_end():
        for item in range(10):
            wait.until(EC.visibility_of_element_located((By.TAG_NAME, "body"))).send_keys(Keys.END)
            time.sleep(1)

    scroll_to_end()

    # title of the video
    title = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="container"]/h1/yt-formatted-string'))).get_attribute(
        "innerText")
    time.sleep(1)

    # Likes of the video
    # likes = driver.find_element(By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a').text
    likes = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="top-level-buttons-computed"]/ytd-toggle-button-renderer[1]/a'))).text
    time.sleep(1)

    # number of comments on the video
    # comment_count = (driver.find_element(By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]')).text
    comment_count = wait.until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="count"]/yt-formatted-string/span[1]'))).text
    time.sleep(1)

    # Comments on the video
    commentNew = driver.find_elements(By.XPATH, '//*[@id="body"]')
    comments = []
    for i in commentNew:
        comments.append({"name": i.find_element(By.CSS_SELECTOR, '#header-author > h3').text,
                         "comment": i.find_element(By.ID, 'comment-content').text})

    # Download video and upload in S3 Bucket and create URL
    if download_video is not None:
        video_s3_URL = handle_S3_videos.handle_videos(url, title)
    else:
        video_s3_URL = 'None'

    details = {'url': url, "title": title, "likes": likes, "number_of_comments": comment_count,
               'thumbnail': f'http://img.youtube.com/vi/{urlparse(url).query[2::]}/maxresdefault.jpg',
               'S3_Bucket_URL': video_s3_URL,
               "comments": comments}

    return details


if __name__ == '__main__':
    app.run()
