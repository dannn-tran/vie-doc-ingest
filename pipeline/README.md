## Development
```sh
uv sync
uv pip install -e .
```

## Example usage

```sh
uv run run-ocr \
  --project-id vie-ocr \
  --input-bucket vie-doc \
  --input-file-prefix "nguyen, duc chinh_2008_van hoa nhiep anh/images" \
  --input-file-exts jpeg \
  --output-bucket vie-doc \
  --output-dir "nguyen, duc chinh_2008_van hoa nhiep anh/ocr" \
  --language-hints vie
    
uv run download-ocr \
  --project-id vie-ocr \
  --src-bucket vie-doc \
  --src-file-prefix "nguyen, duc chinh_2008_van hoa nhiep anh/ocr" \
  --dst-dirpath "/Users/danntran/Repos.nosync/viet-print-index/data/nguyen, duc chinh_2008_van hoa nhiep anh/ocr" \
  --workers 4
```