from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

RAW_TRAIN_PATH = DATA_DIR / "Train.csv"
RAW_DEV_PATH = DATA_DIR / "Dev.csv"
RAW_TEST_PATH = DATA_DIR / "Test.csv"

TRAIN_PATH = PROCESSED_DATA_DIR / "preprocessed_train.csv"
DEV_PATH = PROCESSED_DATA_DIR / "preprocessed_dev.csv"
TEST_PATH = PROCESSED_DATA_DIR / "preprocessed_test.csv"

# Raw dataset columns.
RAW_TEXT_COLUMN = "comment"
RAW_LABEL_COLUMN = "label"

# Text column used by the model scripts after preprocessing.
TEXT_COLUMN = "clean_comment"

# Change these names to match your preprocessed CSV files.
ASPECTS = [
    "GENERAL",
    "SCREEN",
    "CAMERA",
    "FEATURES",
    "BATTERY",
    "PERFORMANCE",
    "STORAGE",
    "DESIGN",
    "PRICE",
    "SER&ACC",
]

# Unified label set for each aspect.
LABELS = ["none", "positive", "neutral", "negative"]

# Extend this dictionary if your preprocessing file uses different label values.
LABEL_MAP = {
    "0": "none",
    "1": "positive",
    "2": "negative",
    "3": "neutral",

    "none": "none",
    "nan": "none",
    "null": "none",
    "": "none",

    "positive": "positive",
    "pos": "positive",
    "p": "positive",

    "negative": "negative",
    "neg": "negative",
    "n": "negative",

    "neutral": "neutral",
    "neu": "neutral",
    "o": "neutral",
}

RANDOM_STATE = 42
