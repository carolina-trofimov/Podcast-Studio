import boto3
import boto

ALLOWED_EXTENSIONS = {"mp3"}

# use Amazon S3
s3 = boto3.resource('s3')
s3_client = s3.meta.client
bucket = s3.Bucket('podcaststudio')
