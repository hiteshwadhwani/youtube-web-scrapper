import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from pytube import YouTube
import os
from urllib.parse import urlparse
import logging_file
import config
def create_connection():
    """Make connection with s3 Bucket
    return: connection string
    """
    # client for S3 Bucket AWS
    try:
        s3_client = boto3.client('s3', region_name='ap-south-1', aws_access_key_id=config.get_aws_access_key_id(),
                                 aws_secret_access_key=config.get_aws_secret_access_key(),
                                 config=Config(signature_version='s3v4'),
                                 endpoint_url='https://s3.ap-south-1.amazonaws.com')
        return s3_client
    except Exception as e:
        logging_file.error(f"some Error in making connection {e}")
        return f"some Error in making connection {e}"


def get_bucket_details(s3_client):
    """return: Return details of S3 Buckets"""
    return s3_client.list_buckets()


# Function for creating URL
def create_presigned_url(s3_client,bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        logging_file.error(f"Error in making URL for {object_name}")
        # logging.error(e)
        return None

    # The response contains the presigned URL
    logging_file.info(f"URL Created for {object_name}")
    return response


def check_video_exist(s3_client, key):
    """Check for key in S3 Bucket
    return: if key not found it will return KNF (key not found)
    """
    try:
        x = s3_client.head_object(Bucket='youtube-scrapper', Key=key)
        return x
    except Exception as e:
        # str(e).split(" ")[3].replace('(', '').replace(')', '')
        logging_file.error(f"{key} not found S3 Bucket {e}")
        return "KNF"  # key not found


def upload_video(s3_client, Filename, Bucket, Key):
    """Upload file in s3 Bucket"""
    try:
        s3_client.upload_fileobj(Filename, Bucket, Key)
        logging_file.info(f"{Key} uploaded in S3 Bucket")
    except Exception as e:
        logging_file.error(f"Some error in Uploading video in S3 Bucket {Key} {e}")
        print(f"some Exception {e}")


def download_videos(url, path='./videos'):
    """Download video from Youtube"""
    try:
        yt = YouTube(str(url))
        yt.streams.filter(progressive=True, file_extension='mp4').first().download(output_path=path,filename=f'{urlparse(url).query[2::]}.mp4')
        logging_file.info(f"Video Downloaded for URL {url}")
    except Exception as e:
        logging_file.error(f"Some error occured in downloading video URL {url} {e}")
        print("some exception", e)


