from fastai.vision.all import *
from pathlib import Path
import torch
import pandas as pd

# -------------------
# CONFIGURATION
# -------------------
DATA_DIR = Path("./dataset")  # should contain 'train' and 'val' folders
NUM_EPOCHS = 10
MODEL_SAVE_PATH = Path("./resnet50_product_multicategory_model.pkl")
BATCH_SIZE = 16
IMG_SIZE = 224  # image size for resizing

# -------------------
# FUNCTION TO EXTRACT LABELS
# -------------------
def get_labels_from_path(path):
    # path = .../train/category/subcategory/image.jpg
    subcategory = path.parent.name
    category = path.parent.parent.name
    return category, subcategory

# -------------------
# MAIN TRAINING
# -------------------
def main():
    print("✅ CUDA available:", torch.cuda.is_available())
    print("✅ Device count:", torch.cuda.device_count())
    if torch.cuda.is_available():
        print("✅ Using GPU:", torch.cuda.get_device_name(0))
    else:
        print("⚠️ Using CPU only")

    # -------------------
    # GET IMAGE FILES AND LABELS
    # -------------------
    splits = GrandparentSplitter(train_name='train', valid_name='val')(get_image_files(DATA_DIR))
    
    items = get_image_files(DATA_DIR)
    labels = [get_labels_from_path(f) for f in items]
    
    df = pd.DataFrame(labels, columns=['category','subcategory'])
    df['fname'] = items

    # -------------------
    # BUILD DATABLOCK
    # -------------------
    dblock = DataBlock(
        blocks=(ImageBlock, MultiCategoryBlock),
        get_x=ColReader('fname'),
        get_y=ColReader(['category','subcategory']),
        splitter=IndexSplitter(splits[1]),
        item_tfms=Resize(IMG_SIZE),
        batch_tfms=aug_transforms(mult=1.0)
    )

    dls = dblock.dataloaders(df, bs=BATCH_SIZE, num_workers=0)

    print(f"Category & Subcategory vocab: {dls.vocab}")
    
    # -------------------
    # CREATE DUAL-OUTPUT MODEL
    # -------------------
    # FastAI supports MultiCategoryBlock, which outputs multi-label one-hot vectors
    learn = vision_learner(
        dls,
        resnet50,
        loss_func=BCEWithLogitsLossFlat(),  # suitable for multi-label classification
        metrics=[accuracy_multi],
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
