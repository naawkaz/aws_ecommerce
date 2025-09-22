import boto3
import psycopg2
from fastai.vision.all import *
import torch
import io
from datetime import datetime

# -------------------
# CONFIG
# -------------------
BUCKET_NAME = "visionrank-product-images"
MODEL_PATH = "./resnet50_product_model.pkl"
DB_CONFIG = {
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": ""
}

# -------------------
# INIT
# -------------------
# AWS S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name="ap-southeast-5"
)
learn = load_learner(MODEL_PATH)
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# -------------------
# FETCH PRODUCT IMAGES FROM DB
# -------------------
cur.execute("SELECT image_id, s3_key FROM product_images;")
rows = cur.fetchall()

print(f"Found {len(rows)} images to process.")

# -------------------
# FUNCTION TO DOWNLOAD IMAGE FROM S3
# -------------------
def download_image(bucket, key):
    obj = s3.get_object(Bucket=bucket, Key=key)
    return PILImage.create(obj["Body"])

# -------------------
# FUNCTION TO GENERATE EMBEDDING
# -------------------
def generate_embedding(img):
    # Prepare batch
    dl = learn.dls.test_dl([img])
    xb = dl.one_batch()[0]  # input tensor

    # Forward pass through model body
    with torch.no_grad():
        # Get pooled embedding (output of AdaptiveAvgPool layer)
        embedding = learn.model[0](xb)
        # If model[0] outputs feature maps, apply avgpool manually:
        if embedding.ndim > 2:
            embedding = torch.nn.functional.adaptive_avg_pool2d(embedding, 1).squeeze(-1).squeeze(-1)
    return embedding.cpu().numpy().flatten()


# -------------------
# LOOP OVER IMAGES
# -------------------
for image_id, s3_key in rows:
    try:
        # 1. Download image
        img = download_image(BUCKET_NAME, s3_key)

        # 2. Generate embedding
        embedding = generate_embedding(img)

        # 3. Insert into DB
        cur.execute("""
            INSERT INTO image_embeddings (image_id, embedding, created_at)
            VALUES (%s, %s, %s);
        """, (image_id, embedding.tolist(), datetime.utcnow()))

        print(f"✅ Inserted embedding for image_id {image_id}")

    except Exception as e:
        print(f"❌ Failed for {image_id}: {e}")
        continue

# Commit and close
conn.commit()
cur.close()
conn.close()
