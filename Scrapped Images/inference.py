import os
import torch
from fastai.vision.all import load_learner, PILImage
import io
import json

def model_fn(model_dir):
    """
    Load FastAI learner from the provided model directory.
    SageMaker automatically passes model_dir when initializing the endpoint.
    """
    model_path = os.path.join(model_dir, "export.pkl")  # change if your file is named differently
    learn = load_learner(model_path)
    learn.model.eval()  # set model to evaluation mode
    return learn

def input_fn(request_body, request_content_type):
    """
    Decode incoming request body into a PILImage.
    """
    if request_content_type == "application/octet-stream":
        return PILImage.create(io.BytesIO(request_body))
    raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """
    Predict subcategory and generate 2048-dim embedding.
    """
    # Predict class
    pred_class = model.predict(input_data)[0]  # returns string label

    # Generate embedding
    with torch.no_grad():
        batch = model.dls.test_dl([input_data]).one_batch()[0]  # apply same transforms as training
        feats = model.model[0](batch)  # forward through ResNet body
        pooled = torch.nn.functional.adaptive_avg_pool2d(feats, 1)  # [1, 2048, 1, 1]
        embedding = pooled.view(pooled.size(0), -1).cpu().numpy().flatten()  # [2048]

    return {
        "subcategory": str(pred_class),
        "embedding": embedding.tolist()
    }

def output_fn(prediction, content_type):
    """
    Convert prediction dict to JSON response.
    """
    if content_type == "application/json":
        return json.dumps(prediction), "application/json"
    raise ValueError(f"Unsupported content type: {content_type}")
