import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def get_ocr_fulltext_one(filepath: str | Path):
    with open(filepath, 'r') as f:
        data = json.load(f)

    return data['fullTextAnnotation']['text']


def extract_ocr_fulltext(src_dir: str, dst_dir: str, workers: int = 4):
    dst_dirpath = Path(dst_dir)
    dst_dirpath.mkdir(exist_ok=True)

    files = Path(src_dir).iterdir()
    if workers < 2:
        for f in files:
            _extract_ocr_fulltext_one(f, dst_dirpath)
        return

    with ThreadPoolExecutor(max_workers=workers) as executor:
        for _ in executor.map(lambda file: _extract_ocr_fulltext_one(file, dst_dirpath), files):
            pass

def _extract_ocr_fulltext_one(src: Path, dst_dirpath: Path):
    text = get_ocr_fulltext_one(src)

    match src.name.rsplit('.', maxsplit=1):
        case [x]:
            filename = x
        case [x, _]:
            filename = x
        case x:
            raise Exception(f"Unexpected split: input={src.name}; output={x}")

    dst = dst_dirpath / (filename + '.txt')
    dst.write_text(text)