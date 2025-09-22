import os
import torch
import torch.nn.functional as F
from fastai.vision.all import load_learner, PILImage
import io
import json
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def model_fn(model_dir):
    """
    Load FastAI learner from the provided model directory.
    """
    try:
        logger.info(f"Loading model from {model_dir}")
        model_path = os.path.join(model_dir, "resnet50_product_model.pkl")
        
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}")
            
        # Load with CPU to avoid GPU issues
        learn = load_learner(model_path, cpu=True)
        logger.info("Model loaded successfully")
        return learn
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def input_fn(request_body, request_content_type):
    """
    Decode incoming request body into a PILImage.
    """
    try:
        if request_content_type == "application/octet-stream":
            return PILImage.create(io.BytesIO(request_body))
        raise ValueError(f"Unsupported content type: {request_content_type}")
    except Exception as e:
        logger.error(f"Error in input_fn: {str(e)}")
        raise

def predict_fn(input_data, model):
    """
    Predict subcategory and generate 2048-dim embedding.
    """
    try:
        logger.info("Starting prediction")
        
        # Get prediction
        with torch.no_grad():
            # Get the DL from learner
            dl = model.dls.test_dl([input_data])
            preds = model.get_preds(dl=dl)
            
            # Get class prediction
            pred_class = model.dls.vocab[preds[0].argmax().item()]
            
            # Get embedding from the second to last layer
            # Access the model's body (ResNet)
            features = model.model[0](dl.one_batch()[0])
            pooled = F.adaptive_avg_pool2d(features, 1)
            embedding = pooled.view(pooled.size(0), -1).cpu().numpy().flatten().tolist()

        logger.info(f"Predicted class: {pred_class}")
        return {
            "subcategory": pred_class,
            "embedding": embedding
        }
    except Exception as e:
        logger.error(f"Error in predict_fn: {str(e)}")
        raise

def output_fn(prediction, content_type):
    """
    Convert prediction dict to JSON response.
    """
    try:
        if content_type == "application/json":
            return json.dumps(prediction), "application/json"
        raise ValueError(f"Unsupported content type: {content_type}")
    except Exception as e:
        logger.error(f"Error in output_fn: {str(e)}")
        raise