import re
import pandas as pd
from collections import Counter

import config

paths = {
    "train": config.RAW_TRAIN_PATH,
    "dev": config.RAW_DEV_PATH,
    "test": config.RAW_TEST_PATH,
}

TEXT_COLUMN = config.RAW_TEXT_COLUMN

emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U00002700-\U000027BF"  # dingbats
    "\U00002600-\U000026FF"  # misc symbols
    "]+",
    flags=re.UNICODE
)

emoticon_pattern = re.compile(
    r"(:\)+|:\(+|:\)+\)+|:\(+\(+|=\)+|=\(+|\^_\^|<3|:v|:D+)",
    flags=re.IGNORECASE
)

rows = []

for split_name, path in paths.items():
    df = pd.read_csv(path)
    counter = Counter()

    if TEXT_COLUMN not in df.columns:
        raise ValueError(
            f"{split_name} does not contain text column '{TEXT_COLUMN}'. "
            f"Available columns: {list(df.columns)}"
        )

    for text in df[TEXT_COLUMN].fillna("").astype(str):
        # Unicode emoji
        for emoji_group in emoji_pattern.findall(text):
            for emoji in emoji_group:
                counter[emoji] += 1

        # Text emoticon
        for emo in emoticon_pattern.findall(text):
            counter[emo] += 1

    for icon, count in counter.items():
        rows.append({
            "split": split_name,
            "icon": icon,
            "count": count
        })

icon_df = pd.DataFrame(rows)

if len(icon_df) == 0:
    print("No emoji/emoticon found.")
    icon_summary = pd.DataFrame(columns=["icon", "count"])
else:
    icon_summary = (
        icon_df
        .groupby("icon", as_index=False)["count"]
        .sum()
        .sort_values("count", ascending=False)
    )

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)

print(icon_summary)