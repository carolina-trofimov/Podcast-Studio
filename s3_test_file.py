import boto3




@app.route("/concatenate-audios", methods=["GET", "POST"])
def concatenate_audios():
    """Allow user to add an ad into a podcast audio"""

    user = User.query.get(session["logged_in_user"])
    #instantiate audio object as pod to access podcast name to concatenate
    pod_id = request.form.get("raw_pod_id")
    pod = Audio.query.get(pod_id)

    file1 = io.BytesIO()
    test = s3.Object("podcaststudio", "raw_podcasts/raw_pod_test2.mp3").download_fileobj(file1)
   
    audio1 = AudioSegment.from_mp3(file1)







# s3 = boto3.client('s3')

# s3 = boto3.client('s3')
# buckets = s3.list_buckets()  #this is a dictionary



# print(buckets)


# # # Let's use Amazon S3
s3 = boto3.resource('s3')  
bucket = s3.Bucket('podcaststudio')  #output >>> s3.Bucket(name='podcaststudio')
print(bucket.name) #output >>> podcaststudio

# # bucket = s3.buckets.all()
# print(bucket) # this is what prints >>> s3.bucketsCollection(s3.ServiceResource(), s3.Bucket)



# for bucket in s3.buckets.all():
#     my_bucket = bucket 
#     print(my_bucket) #output >>> s3.Bucket(name='podcaststudio')
#     print(my_bucket.name) # output  >>> podcaststudio
# #     


# # Retrieve the list of existing buckets
# s3 = boto3.client('s3')
# response = s3.list_buckets()

# # Output the bucket names
# print('Existing buckets:')
# for bucket in response['Buckets']:
#     print(f'  {bucket["Name"]}')


# def create_bucket(bucket_name, region=None):
#     """Create an S3 bucket in a specified region

#     If a region is not specified, the bucket is created in the S3 default
#     region (us-east-1).

#     :param bucket_name: Bucket to create
#     :param region: String region to create bucket in, e.g., 'us-west-2'
#     :return: True if bucket created, else False
#     """

#     # Create bucket
#     try:
#         if region is None:
#             s3_client = boto3.client('s3')
#             s3_client.create_bucket(Bucket=bucket_name)
#         else:
#             s3_client = boto3.client('s3', region_name=region)
#             location = {'LocationConstraint': region}
#             s3_client.create_bucket(Bucket=bucket_name,
#                                     CreateBucketConfiguration=location)
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True


# import logging
# import boto3
# from botocore.exceptions import ClientError


# def upload_file(file_name, bucket, object_name=None):
#     """Upload a file to an S3 bucket

#     :param file_name: File to upload
#     :param bucket: Bucket to upload to
#     :param object_name: S3 object name. If not specified then file_name is used
#     :return: True if file was uploaded, else False
#     """

#     # If S3 object_name was not specified, use file_name
#     if object_name is None:
#         object_name = file_name

#     # Upload the file
#     s3_client = boto3.client('s3')
#     try:
#         response = s3_client.upload_file(file_name, bucket, object_name)
#     except ClientError as e:
#         logging.error(e)
#         return False
#     return True
