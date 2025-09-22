# Simple test script to verify basic functionality
import boto3
from sagemaker.pytorch import PyTorchModel
import sagemaker

# Use the correct region consistently
REGION = "ap-southeast-1"  # Make sure this matches your S3 bucket region!

boto_session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name=REGION
)

sagemaker_session = sagemaker.Session(boto_session=boto_session)

# Test if bucket exists in the same region
s3 = boto_session.client('s3')
try:
    bucket_region = s3.get_bucket_location(Bucket='visionrank-classification-model')['LocationConstraint']
    print(f"Bucket region: {bucket_region}")
    print(f"SageMaker region: {REGION}")
    
    if bucket_region != REGION:
        print("⚠️  WARNING: Bucket and SageMaker are in different regions!")
        print("This will cause performance issues and timeouts!")
        
except Exception as e:
    print(f"Error accessing bucket: {e}")