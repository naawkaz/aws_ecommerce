import os
import shutil
import random
from pathlib import Path

# -------------------
# CONFIGURATION
# -------------------
SOURCE_DIR = Path("./Data Collection")  # your original images folder: category/subcategory/images
DATASET_DIR = Path("./dataset")              # dataset folder to be created
TRAIN_RATIO = 0.7
VAL_RATIO = 0.2
TEST_RATIO = 0.1
RANDOM_SEED = 42

# -------------------
# DELETE OLD DATASET FOLDER
# -------------------
if DATASET_DIR.exists():
    print(f"Removing old dataset folder: {DATASET_DIR}")
    shutil.rmtree(DATASET_DIR)

# -------------------
# CREATE NEW FOLDER STRUCTURE
# -------------------
for split in ["train", "val", "test"]:
    (DATASET_DIR / split).mkdir(parents=True, exist_ok=True)

# -------------------
# COPY FILES WITH RANDOM SPLIT
# -------------------
random.seed(RANDOM_SEED)

for category_dir in SOURCE_DIR.iterdir():
    if category_dir.is_dir():
        category_name = category_dir.name
        for subcategory_dir in category_dir.iterdir():
            if subcategory_dir.is_dir():
                subcategory_name = subcategory_dir.name
                
                # Create subfolders in train/val/test
                for split in ["train", "val", "test"]:
                    target_dir = DATASET_DIR / split / subcategory_name
                    target_dir.mkdir(parents=True, exist_ok=True)
                
                # List all images
                images = [f for f in subcategory_dir.iterdir() if f.is_file()]
                random.shuffle(images)
                
                num_images = len(images)
                train_end = int(num_images * TRAIN_RATIO)
                val_end = train_end + int(num_images * VAL_RATIO)
                
                # Split images
                splits = {
                    "train": images[:train_end],
                    "val": images[train_end:val_end],
                    "test": images[val_end:]
                }
                
                # Copy files to target folders
                for split, files in splits.items():
                    for img_path in files:
                        dest_path = DATASET_DIR / split / subcategory_name / img_path.name
                        shutil.copy2(img_path, dest_path)

print("✅ Dataset folder created with train, val, test splits.")
