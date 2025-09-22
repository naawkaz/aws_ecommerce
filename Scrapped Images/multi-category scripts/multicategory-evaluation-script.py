from fastai.vision.all import *
from pathlib import Path
from collections import defaultdict
import torch
import pandas as pd

# -------------------
# CONFIGURATION
# -------------------
DATASET_DIR = Path("./dataset")
MODEL_PATH = Path("./resnet50_product_multicategory_model.pkl")
IMG_SIZE = 224
BATCH_SIZE = 16

# -------------------
# HELPER: extract labels from path
# -------------------
def get_labels_from_path(path):
    # path = .../test/category/subcategory/image.jpg
    subcategory = path.parent.name
    category = path.parent.parent.name
    return category, subcategory

# -------------------
# MAIN EVALUATION
# -------------------
def main():
    # -------------------
    # Prepare test DataFrame
    # -------------------
    test_files = get_image_files(DATASET_DIR/"test")
    labels = [get_labels_from_path(f) for f in test_files]
    
    df_test = pd.DataFrame(labels, columns=['category','subcategory'])
    df_test['fname'] = test_files

    # -------------------
    # Load the trained model
    # -------------------
    learn = load_learner(MODEL_PATH)

    # -------------------
    # Build a test DataLoader
    # -------------------
    dblock = DataBlock(
        blocks=(ImageBlock, MultiCategoryBlock),
        get_x=ColReader('fname'),
        get_y=ColReader(['category','subcategory']),
        item_tfms=Resize(IMG_SIZE)
    )

    test_dl = dblock.dataloaders(df_test, bs=BATCH_SIZE, num_workers=0).train

    # -------------------
    # Get predictions
    # -------------------
    preds, y_true = learn.get_preds(dl=test_dl)
    
    # Multi-hot → class indices
    y_pred = preds.argmax(dim=1)
    y_true_indices = y_true.argmax(dim=1)

    # Vocabulary
    vocab = learn.dls.vocab
    num_categories = len(set(df_test['category']))
    num_subcategories = len(set(df_test['subcategory']))

    category_names = vocab[:num_categories]
    subcategory_names = vocab[num_categories:]

    category_pred = y_pred // num_subcategories
    subcategory_pred = y_pred % num_subcategories

    category_true = y_true_indices // num_subcategories
    subcategory_true = y_true_indices % num_subcategories

    # -------------------
    # Accuracy reporting
    # -------------------
    def accuracy_report(y_t, y_p, class_names, label_type="Label"):
        total_correct = (y_t == y_p).sum().item()
        total_samples = len(y_t)
        overall_acc = total_correct / total_samples * 100
        print(f"\n📊 {label_type} - Overall Accuracy: {overall_acc:.2f}% ({total_correct}/{total_samples})")

        per_class_correct = defaultdict(int)
        per_class_total = defaultdict(int)
        for yt, yp in zip(y_t, y_p):
            class_name = class_names[int(yt)]
            per_class_total[class_name] += 1
            if yt == yp:
                per_class_correct[class_name] += 1

        print(f"\n📌 {label_type} - Per-Class Accuracy:")
        for cls in class_names:
            correct = per_class_correct[cls]
            total = per_class_total[cls]
            if total > 0:
                acc = correct / total * 100
                print(f"{cls:20s}: {acc:.2f}% ({correct}/{total})")
            else:
                print(f"{cls:20s}: No samples in test set")

    # -------------------
    # Print reports
    # -------------------
    accuracy_report(category_true, category_pred, category_names, label_type="Category")
    accuracy_report(subcategory_true, subcategory_pred, subcategory_names, label_type="Subcategory")

# -------------------
# Windows-safe entry point
# -------------------
if __name__ == "__main__":
    main()
