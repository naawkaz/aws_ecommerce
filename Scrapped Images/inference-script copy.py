import os
import torch
from fastai.vision.all import load_learner, PILImage
import io
import json

def model_fn(model_dir):
    """Load model for SageMaker endpoint"""
    model_path = os.path.join(model_dir, "export.pkl")
    learn = load_learner(model_path)
    learn.model.eval()  # ensure eval mode
    return learn

def input_fn(request_body, request_content_type):
    """Decode incoming request"""
    if request_content_type == "application/octet-stream":
        return io.BytesIO(request_body)
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Generate embedding and class prediction"""
    img = PILImage.create(input_data)
    pred_class, pred_idx, outputs = model.predict(img)

    # -------------------------------
    # Generate embedding properly
    # -------------------------------
    dl = model.dls.test_dl([img])
    xb = dl.one_batch()[0]  # get the input tensor
    with torch.no_grad():
        # Forward pass through the CNN body
        feat_maps = model.model[0](xb)

        # If output is a 4D feature map, apply adaptive average pooling
        if feat_maps.ndim == 4:  # (B, C, H, W)
            embedding = torch.nn.functional.adaptive_avg_pool2d(feat_maps, 1)
            embedding = embedding.view(embedding.size(0), -1)  # flatten to (B, C)
        else:
            embedding = feat_maps

    embedding = embedding.cpu().numpy().flatten()

    return {"subcategory": str(pred_class), "embedding": embedding.tolist()}

def output_fn(prediction, content_type):
    """Return JSON"""
    if content_type == "application/json":
        return json.dumps(prediction), "application/json"
    raise ValueError(f"Unsupported content type: {content_type}")
