from fastai.vision.all import *
from pathlib import Path
import torch

# -------------------
# CONFIGURATION
# -------------------
DATA_DIR = Path("./dataset")  # should contain 'train' and 'val' folders
NUM_EPOCHS = 10
MODEL_SAVE_PATH = Path("./resnet50_product_model.pkl")
BATCH_SIZE = 16
IMG_SIZE = 224  # image size for resizing

def main():

    print("✅ CUDA available:", torch.cuda.is_available())
    print("✅ Device count:", torch.cuda.device_count())
    if torch.cuda.is_available():
        print("✅ Using GPU:", torch.cuda.get_device_name(0))
    else:
        print("⚠️ Using CPU only")
        
    # -------------------
    # DATASET & DATALOADER
    # -------------------
    dls = ImageDataLoaders.from_folder(
        DATA_DIR,
        train='train',
        valid='val',
        valid_pct=None,      # already have separate validation folder
        item_tfms=Resize(IMG_SIZE),
        batch_tfms=aug_transforms(mult=1.0),
        bs=BATCH_SIZE,
        num_workers=0  # ✅ safer on Windows, avoids multiprocessing issues
    )

    print(f"Classes: {dls.vocab}")
    print(f"Number of classes: {len(dls.vocab)}")

    # -------------------
    # MODEL SETUP
    # -------------------
    learn = vision_learner(
        dls,
        resnet50,
        metrics=accuracy,
        pretrained=True
    )

    # -------------------
    # TRAINING
    # -------------------
    learn.fine_tune(NUM_EPOCHS)

    # -------------------
    # SAVE MODEL
    # -------------------
    learn.export(MODEL_SAVE_PATH)
    print(f"✅ Model saved to {MODEL_SAVE_PATH}")

# Windows-safe entry point
if __name__ == "__main__":
    main()
