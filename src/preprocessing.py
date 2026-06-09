import csv
import math
import re
import unicodedata

import config

TEENCODE_MAP = {
    # Basic agreement / common words
    "okie": "ok",
    "okey": "ok",
    "ôkê": "ok",
    "oki": "ok",
    "oke": "ok",
    "okay": "ok",
    "okê": "ok",

    # Negation
    "kg": "không",
    "not": "không",
    "k": "không",
    "kh": "không",
    "kô": "không",
    "hok": "không",
    "ko": "không",
    "khong": "không",
    "hem": "không",
    "kp": "không phải",

    # Thanks / informal words
    "tks": "cảm ơn",
    "thks": "cảm ơn",
    "thanks": "cảm ơn",
    "ths": "cảm ơn",
    "thank": "cảm ơn",
    "hùi đó": "hồi đó",
    "mún": "muốn",

    # Positive sentiment / slang
    "perfect": "rất tốt",
    "cute": "dễ thương",
    "iu": "yêu",
    "thik": "thích",
    "thick": "thích",

    "gud": "tốt",
    "good": "tốt",
    "gút": "tốt",
    "tot": "tốt",
    "nice": "tốt",
    "hehe": "tốt",
    "hihi": "tốt",
    "haha": "tốt",
    "hjhj": "tốt",
    "^_^": "tốt",

    # Neutral / normal
    "bt": "bình thường",
    "bthg": "bình thường",

    # Negative sentiment / slang
    "lol": "không tốt",
    "cc": "không tốt",
    "huhu": "không tốt",
    "sad": "tệ",
    "por": "tệ",
    "poor": "tệ",
    "bad": "tệ",
    "fake": "giả mạo",

    # Degree / function words
    "wa": "quá",
    "wá": "quá",
    "qá": "quá",
    "đx": "được",
    "dk": "được",
    "dc": "được",
    "đk": "được",
    "đc": "được",
    "duoc": "được",
    "vs": "với",
    "j": "gì",
    "r": "rồi",
    "m": "mình",
    "mik": "mình",
    "mk": "mình",
    "time": "thời gian",
    "h": "giờ",

    # Product-review-specific terms
    "hàg": "hàng",
    "cx": "cũng",
    "cug": "cũng",
    "cung": "cũng",
    "sp": "sản phẩm",
    "dt": "điện thoại",
    "đt": "điện thoại",
    "mn": "mọi người",
    "nv": "nhân viên",
    "sd": "sử dụng",
    "sài": "xài",
    "sai": "xài",
    "wf": "wifi",
    "bin": "pin",

    # Icons and emoticons found in the raw splits by list_icons.py
        # Icons and emoticons found in the raw splits by list_icons.py

    # Positive / satisfied icons
    "👍": "tốt",
    "😂": "tốt",
    "😊": "tốt",
    "😍": "rất tốt",
    "❤": "rất tốt",
    "❤️": "rất tốt",
    "♥": "rất tốt",
    "😁": "tốt",
    "👌": "tốt",
    "😘": "rất tốt",
    "😄": "tốt",
    "😅": "tốt",
    "😆": "tốt",
    "😉": "tốt",
    "☺": "tốt",
    "😀": "tốt",
    "😌": "tốt",
    "😚": "rất tốt",
    "😎": "tốt",
    "😋": "tốt",
    "😃": "tốt",
    "😙": "rất tốt",
    "🙂": "tốt",
    "👏": "tốt",
    "💯": "rất tốt",
    "💓": "rất tốt",
    "👋": "tốt",
    "🙃": "tốt",
    "🙆": "tốt",
    "💪": "tốt",
    "💙": "rất tốt",
    "💌": "rất tốt",
    "😗": "rất tốt",
    "🎉": "tốt",
    "☆": "tốt",
    "✓": "tốt",

    # Negative / dissatisfied icons
    "😭": "không tốt",
    "😑": "không tốt",
    "😪": "không tốt",
    "😔": "không tốt",
    "😒": "không tốt",
    "😢": "không tốt",
    "😥": "không tốt",
    "😣": "không tốt",
    "😡": "không tốt",
    "😩": "không tốt",
    "😟": "không tốt",
    "👎": "không tốt",
    "😞": "không tốt",
    "☹": "không tốt",
    "😐": "bình thường",
    "😏": "không tốt",
    "☠": "không tốt",
    "😓": "không tốt",
    "😫": "không tốt",
    "😝": "không tốt",
    "😰": "không tốt",
    "🙄": "không tốt",
    "😱": "không tốt",
    "💔": "không tốt",
    "😕": "không tốt",
    "😠": "không tốt",
    "😵": "không tốt",
    "😬": "không tốt",
    "🙁": "không tốt",
    "😷": "không tốt",
    "😶": "không tốt",

    # Product / aspect-related icons
    "🔋": "pin",
    "📸": "camera",
    "🎧": "tai nghe",
    "🎮": "game",
    "🔊": "loa",
    "📱": "điện thoại",
    "💰": "giá",
    "💴": "giá",
    "💧": "nước",
    "🐃": "trâu",
    "🐄": "bò",
    "🐠": "cá",
    "🍊": "cam",

    # Icons that are usually not useful for ABSA
    "🏻": "",
    "🇳": "",
    "🇻": "",
    "♀": "",
    "✋": "",
    "👹": "",
    "😈": "",
    "🙉": "",
}


_WORD_RE = re.compile(r"\b\w+\b", flags=re.UNICODE)


def normalize_repeated_chars(text: str) -> str:
    """Collapse long repeated character runs, e.g. 'trâuuu' -> 'trâu'."""
    return re.sub(r"(.)\1{2,}", r"\1", text)


def normalize_teencode(text: str) -> str:
    if not text:
        return ""

    # Normalize repeated text emoticons.
    # Examples:
    # :), :)), :))), :)))))))) -> tốt
    # :(, :((, :((((          -> không tốt
    # =), =)), =))))          -> tốt
    # =((                     -> không tốt
    text = re.sub(r":\)+", " tốt ", text)
    text = re.sub(r"=\)+", " tốt ", text)
    text = re.sub(r":d+", " tốt ", text, flags=re.IGNORECASE)
    text = re.sub(r":v", " tốt ", text, flags=re.IGNORECASE)
    text = re.sub(r":\(+", " không tốt ", text)
    text = re.sub(r"=\(+", " không tốt ", text)
    text = re.sub(r"<3", " rất tốt ", text)

    # 1. Replace symbol-based variants first.
    symbol_variants = {
        variant: normalized
        for variant, normalized in TEENCODE_MAP.items()
        if not re.fullmatch(r"\w+", variant, flags=re.UNICODE)
    }

    for variant, normalized in sorted(symbol_variants.items(), key=lambda x: len(x[0]), reverse=True):
        text = text.replace(variant, f" {normalized} ")

    # 2. Replace word-like variants.
    def replace_token(match: re.Match[str]) -> str:
        token = match.group(0)
        return TEENCODE_MAP.get(token, token)

    text = _WORD_RE.sub(replace_token, text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def clean_text(text: str) -> str:
    """
    Clean and normalize Vietnamese review text.

    Processing order:
    1. Unicode normalization
    2. Lowercase
    3. Normalize teencode / emoji / emoticon
    4. Normalize repeated characters
    5. Remove remaining special characters
    6. Normalize whitespace
    """
    if text is None:
        return ""

    text = unicodedata.normalize("NFC", str(text))
    text = text.lower().strip()

    # Must be before punctuation removal to preserve symbols like ':)', '😍', '👍'.
    text = normalize_teencode(text)

    text = normalize_repeated_chars(text)

    # Remove remaining punctuation and special characters.
    # Vietnamese letters, digits, underscores and whitespace are kept.
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_text(text: str) -> str:
    return clean_text(text)


def normalize_text(text: str) -> str:
    return clean_text(text)


def is_missing(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def normalize_label(value) -> str:
    if is_missing(value):
        return "none"

    value = str(value).strip().lower()

    if value in config.LABEL_MAP:
        return config.LABEL_MAP[value]

    raise ValueError(
        f"Unknown label value: {value}. Please update LABEL_MAP in config.py."
    )


def parse_aspect_labels(label_value) -> dict[str, str]:
    """
    Parse labels from raw UIT-ViSFD format.

    Example:
    "{CAMERA#Positive};{BATTERY#Negative};{OTHERS};"

    Output:
    {
        "CAMERA": "positive",
        "BATTERY": "negative",
        other_aspects: "none"
    }

    OTHERS is ignored because it does not contain aspect-level sentiment.
    """
    labels = {aspect: "none" for aspect in config.ASPECTS}

    if is_missing(label_value):
        return labels

    aspect_lookup = {aspect.upper(): aspect for aspect in config.ASPECTS}
    label_text = str(label_value)
    matches = re.findall(r"\{([^#{};]+)(?:#([^{};]+))?\}", label_text)

    for raw_aspect, raw_sentiment in matches:
        aspect_key = raw_aspect.strip().upper()

        if aspect_key == "OTHERS" or aspect_key not in aspect_lookup:
            continue

        if not raw_sentiment:
            continue

        aspect = aspect_lookup[aspect_key]
        labels[aspect] = normalize_label(raw_sentiment)

    return labels


def validate_raw_columns(fieldnames: list[str], split_name: str) -> None:
    required_columns = [config.RAW_TEXT_COLUMN, config.RAW_LABEL_COLUMN]
    missing = [col for col in required_columns if col not in fieldnames]

    if missing:
        raise ValueError(
            f"{split_name} is missing columns: {missing}\n"
            f"Available columns: {fieldnames}\n"
            f"Please update RAW_TEXT_COLUMN and RAW_LABEL_COLUMN in config.py."
        )


def preprocess_row(row: dict[str, str]) -> dict[str, str]:
    processed_row = dict(row)
    processed_row[config.TEXT_COLUMN] = clean_text(row.get(config.RAW_TEXT_COLUMN, ""))
    processed_row.update(parse_aspect_labels(row.get(config.RAW_LABEL_COLUMN)))
    return processed_row


def build_output_columns(input_columns: list[str]) -> list[str]:
    output_columns = list(input_columns)

    for column in [config.TEXT_COLUMN] + config.ASPECTS:
        if column not in output_columns:
            output_columns.append(column)

    return output_columns


def preprocess_file(input_path, output_path, split_name: str) -> int:
    if not input_path.exists():
        raise FileNotFoundError(
            f"{split_name} file not found: {input_path}\n"
            f"Please place the raw CSV at this path or update config.py."
        )

    with open(input_path, newline="", encoding="utf-8-sig") as input_file:
        reader = csv.DictReader(input_file)
        input_columns = reader.fieldnames or []
        validate_raw_columns(input_columns, split_name)
        output_columns = build_output_columns(input_columns)
        processed_rows = [preprocess_row(row) for row in reader]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", newline="", encoding="utf-8-sig") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(processed_rows)

    return len(processed_rows)


def preprocess_all_splits() -> None:
    splits = [
        ("train", config.RAW_TRAIN_PATH, config.TRAIN_PATH),
        ("dev", config.RAW_DEV_PATH, config.DEV_PATH),
        ("test", config.RAW_TEST_PATH, config.TEST_PATH),
    ]

    for split_name, input_path, output_path in splits:
        row_count = preprocess_file(input_path, output_path, split_name)
        print(f"Saved {split_name} split: {output_path} ({row_count} rows)")


def main() -> None:
    preprocess_all_splits()


if __name__ == "__main__":
    main()
