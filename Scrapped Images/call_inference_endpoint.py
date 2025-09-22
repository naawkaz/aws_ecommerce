import boto3
import json
import time

endpoint_name = "visionrank-inferencing-v4"

runtime = boto3.client(
    'sagemaker-runtime',
    region_name="ap-southeast-1",
    aws_access_key_id="",
    aws_secret_access_key=""
)

def infer_image_sagemaker(image_path):
    with open(image_path, "rb") as f:
        payload = f.read()

    try:
        start_time = time.time()
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType="application/octet-stream",
            Body=payload
        )
        
        result = response['Body'].read()
        end_time = time.time()
        print(f"Inference took {end_time - start_time:.2f} seconds")
        
        prediction = json.loads(result)
        return prediction
        
    except Exception as e:
        print(f"Error calling endpoint: {str(e)}")
        return None

# Example usage
res = infer_image_sagemaker("Data collection/shoe/sneakers/sneakers_1.jpg")
if res:
    print(res)
else:
    print("Inference failed")