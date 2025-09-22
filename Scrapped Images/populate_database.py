import os
import uuid
import random
import boto3
import psycopg2
from faker import Faker
from datetime import datetime
from pathlib import Path

# -------------------
# CONFIGURATION
# -------------------
BUCKET_NAME = "visionrank-product-images"
LOCAL_IMAGE_DIR = "Data collection"  # parent folder of category dirs
DB_CONFIG = {
    "host": "",
    "port": 5432,
    "database": "",
    "user": "",
    "password": ""
}

# AWS S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name="ap-southeast-5"
)

# Faker instance
faker = Faker()

# Aurora DB connection
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# -------------------
# HELPER FUNCTIONS
# -------------------

def upload_to_s3(local_path, s3_key):
    """Upload a file to S3 and return the S3 key."""
    s3.upload_file(local_path, BUCKET_NAME, s3_key)
    return s3_key

def insert_product(name, brand, category, subcategory, description, price, rating):
    """Insert a product and return its ID."""
    cursor.execute("""
        INSERT INTO products (name, brand, product_category, product_subcategory, description, price, rating, available, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE, NOW())
        RETURNING product_id;
    """, (name, brand, category, subcategory, description, price, rating))
    return cursor.fetchone()[0]

def insert_product_image(product_id, s3_key):
    """Insert product image record (image_id is auto-generated)."""
    cursor.execute("""
        INSERT INTO product_images (product_id, s3_key, created_at)
        VALUES (%s, %s, NOW());
    """, (product_id, s3_key))

# -------------------
# MAIN LOGIC
# -------------------
def populate():
    for category_dir in Path(LOCAL_IMAGE_DIR).iterdir():
        if category_dir.is_dir():
            category = category_dir.name
            for subcategory_dir in category_dir.iterdir():
                if subcategory_dir.is_dir():
                    subcategory = subcategory_dir.name
                    count = 1
                    for image_file in subcategory_dir.glob("*.*"):  # jpg/png/etc.
                        # Mock product data
                        brand = faker.company().split(" ")[0]  # shorter brand name
                        product_name = f"{brand} {subcategory.capitalize()} {count}"
                        description = faker.text(max_nb_chars=100)
                        price = round(random.uniform(100.0, 1000.0), 2)
                        rating = round(random.uniform(0.0, 5.0), 1)

                        # Insert product
                        product_id = insert_product(
                            product_name, brand, category, subcategory,
                            description, price, rating
                        )

                        # Upload image to S3
                        s3_key = f"{category}/{subcategory}/{image_file.name}"
                        upload_to_s3(str(image_file), s3_key)

                        # Insert product image record
                        insert_product_image(product_id, s3_key)

                        print(f"Inserted product {product_name} with image {s3_key}")
                        count += 1

    # Commit all inserts
    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All products and images uploaded successfully.")

# -------------------
# RUN
# -------------------
if __name__ == "__main__":
    populate()
