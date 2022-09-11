from dotenv import load_dotenv
import os


def configure():
    load_dotenv()


def get_aws_access_key_id():
    return os.environ["aws_access_key_id"]


def get_aws_secret_access_key():
    return os.environ["aws_secret_access_key"]


def get_mongodb_pass():
    return os.environ["mongodb_pass"]
