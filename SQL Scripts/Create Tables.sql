-- Table: products
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT,
    product_type TEXT,
    description TEXT,
    price NUMERIC(10,2),
    available BOOLEAN DEFAULT TRUE,
	created_at TIMESTAMP DEFAULT NOW()
);

-- Table: product_images
CREATE TABLE product_images (
    image_id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(product_id) ON DELETE CASCADE,
    s3_key TEXT NOT NULL, -- S3 object key (not full URL)
    created_at TIMESTAMP DEFAULT NOW()
);

-- pgvector extension (must enable once)
CREATE EXTENSION IF NOT EXISTS vector;

-- Table: image_embeddings
CREATE TABLE image_embeddings (
    embedding_id SERIAL PRIMARY KEY,
    image_id INT REFERENCES product_images(image_id) ON DELETE CASCADE,
    embedding vector(768), -- 768 is typical for CLIP/ViT embeddings
    created_at TIMESTAMP DEFAULT NOW()
);

SELECT * FROM image_embeddings