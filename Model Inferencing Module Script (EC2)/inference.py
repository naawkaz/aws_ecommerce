from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastai.vision.all import load_learner, PILImage
import numpy as np
import os
from uuid import uuid4

# Initialize FastAPI
app = FastAPI(title="VisionRank Inference API")

# Load trained model
MODEL_PATH = "resnet50_product_model.pkl"
learn = load_learner(MODEL_PATH)

# Temporary folder for uploaded images
UPLOAD_FOLDER = "temp_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper function to generate embedding
def get_embedding(img: PILImage):
    # Forward pass to extract embedding
    # fastai Learner has model object
    with learn.model.eval():
        xb = learn.dls.test_dl([img]).one_batch()[0]  # get batch tensor
        embedding = learn.model(xb).detach().cpu().numpy().flatten()
    return embedding.tolist()

# API endpoint for prediction
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        # Save uploaded image temporarily
        file_ext = file.filename.split(".")[-1]
        file_id = str(uuid4())
        temp_file_path = os.path.join(UPLOAD_FOLDER, f"{file_id}.{file_ext}")

        with open(temp_file_path, "wb") as f:
            f.write(await file.read())

        # Load image
        img = PILImage.create(temp_file_path)

        # Predict class
        pred, pred_idx, probs = learn.predict(img)
        subcategory = str(pred)
        
        # Generate embedding
        embedding = get_embedding(img)

        # Clean up temporary image
        os.remove(temp_file_path)

        # Return JSON response
        return JSONResponse(
            content={
                "subcategory": subcategory,
                "embedding": embedding
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

# Optional: Health check
@app.get("/health")
def health():
    return {"status": "ok"}
