from fastai.vision.all import *
from pathlib import Path
from collections import defaultdict
import torch

DATASET_DIR = Path("./dataset")
MODEL_PATH = Path("./resnet50_product_model.pkl")

def main():
    # --------------------
    # LOAD TEST DATALOADER (with labels from subfolders)
    # --------------------
    test_dls = ImageDataLoaders.from_folder(
        DATASET_DIR,
        train="test",      # only for loading
        valid_pct=0.0,     # no split
        item_tfms=Resize(224),
        batch_tfms=aug_transforms(),
        num_workers=0
    )
    test_dl = test_dls.train  # all images with labels

    # --------------------
    # LOAD MODEL
    # --------------------
    learn = load_learner(MODEL_PATH)

    # --------------------
    # PREDICT ON TEST SET
    # --------------------
    preds, y_true = learn.get_preds(dl=test_dl)
    y_pred = preds.argmax(dim=1)
    classes = test_dl.vocab

    # --------------------
    # CALCULATE ACCURACY
    # --------------------
    y_true = torch.tensor(y_true)
    y_pred = torch.tensor(y_pred)

    total_correct = (y_pred == y_true).sum().item()
    total_samples = len(y_true)
    overall_acc = total_correct / total_samples * 100
    print(f"\n📊 Overall Accuracy: {overall_acc:.2f}% ({total_correct}/{total_samples})\n")

    # --------------------
    # PER-CLASS ACCURACY
    # --------------------
    per_class_correct = defaultdict(int)
    per_class_total = defaultdict(int)
    for yt, yp in zip(y_true, y_pred):
        class_name = classes[int(yt)]
        per_class_total[class_name] += 1
        if yt == yp:
            per_class_correct[class_name] += 1

    print("📌 Per-Class Accuracy:\n")
    for cls in classes:
        correct = per_class_correct[cls]
        total = per_class_total[cls]
        if total > 0:
            acc = correct / total * 100
            print(f"{cls:20s}: {acc:.2f}% ({correct}/{total})")
        else:
            print(f"{cls:20s}: No samples in test set")

if __name__ == "__main__":
    main()
