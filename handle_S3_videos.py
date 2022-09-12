import os
import shutil
import S3bucket
from urllib.parse import urlparse
import logging_file


def reset_directory():
    target_path = './videos'
    if os.path.exists(target_path):
        shutil.rmtree(target_path)
    logging_file.info("directory /videos reset")
    os.mkdir(target_path)



# def handle_videos(url,title):
#     conn_string = S3bucket.create_connection()
#
#     if S3bucket.check_video_exist(conn_string,title) == 'KNF':
#
#         S3bucket.download_videos(url)
#         id = urlparse(url).query[2::]
#         path = os.path.join(os.path.dirname(__file__), 'videos', f"{id}.mp4").replace('\\', '/')
#         # Then we will upload video
#         with open(path, 'rb') as file:
#             S3bucket.upload_video(conn_string, file, 'youtube-scrapper', f"{title}.mp4")
#
#     try:
#         return S3bucket.create_presigned_url(conn_string, 'youtube-scrapper', f"{title}.mp4")
#     except Exception as e:
#         logging_file.error(f"Some error In making URL {e}")
#         print(f"Some Exception occurred {e}")

def handle_videos(url):
    conn_string = S3bucket.create_connection()
    S3bucket.download_videos(url)
    id = urlparse(url).query[2::]
    path = os.path.join(os.path.dirname(__file__), 'videos', f"{id}.mp4").replace('\\', '/')
    # Then we will upload video
    with open(path, 'rb') as file:
        S3bucket.upload_video(conn_string, file, 'youtube-scrapper', f"{id}.mp4")
    try:
        return S3bucket.create_presigned_url(conn_string, 'youtube-scrapper', f"{id}.mp4")
    except Exception as e:
        logging_file.error(f"Some error In making URL {e}")
        print(f"Some Exception occurred {e}")


