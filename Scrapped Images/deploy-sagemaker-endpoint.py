import boto3
import sagemaker
from sagemaker.pytorch import PyTorchModel
import time

# AWS session - NOTE: Remove these hardcoded credentials before production!
# Use IAM roles, environment variables, or AWS credentials file instead
AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
REGION = "ap-southeast-1"  # Changed to valid region

# Create boto3 session
boto_session = boto3.Session(
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=REGION
)

# SageMaker session
sagemaker_session = sagemaker.Session(boto_session=boto_session)

# IAM role for SageMaker
role = "arn:aws:iam::484870651864:role/visionrank-sagemaker"

# S3 bucket and model configuration
bucket_name = "visionrank-classify-model"
model_key = "model.tar.gz"  # Model should be packaged as tar.gz

# The model data should be packaged as model.tar.gz containing:
# - your model file (resnet50_product_model.pkl)
# - inference-script.py
# - any dependencies/requirements

try:
    # Create a PyTorchModel

    pytorch_model = PyTorchModel(
        entry_point="inference.py",
        # source_dir="code",  # This tells SageMaker to look in the code directory
        role=role,
        framework_version="1.13.1",
        py_version="py39",
        model_data=f"s3://{bucket_name}/{model_key}",
        sagemaker_session=sagemaker_session
    )
    
    endpoint_name = "visionrank-inferencing-v4"

    print(f"Starting deployment of endpoint: {endpoint_name}")

    # Deploy as a real-time endpoint
    predictor = pytorch_model.deploy(
        instance_type="ml.g4dn.xlarge",
        initial_instance_count=1,
        endpoint_name=endpoint_name,
        wait=True  # Wait for deployment to complete
    )

    print(f"Endpoint successfully deployed: {predictor.endpoint_name}")
    print(f"Endpoint URL: {predictor.endpoint_name}")

except Exception as e:
    print(f"Deployment failed with error: {str(e)}")
    
    # Clean up if deployment fails
    try:
        client = boto_session.client('sagemaker')
        client.delete_endpoint(EndpointName=endpoint_name)
        client.delete_endpoint_config(EndpointConfigName=endpoint_name)
        print("Cleaned up failed deployment resources")
    except:
        pass