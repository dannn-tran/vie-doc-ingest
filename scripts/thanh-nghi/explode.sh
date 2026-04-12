#!/bin/bash

shopt -s nullglob

mkdir -p images

for pdf_filepath in pdf/*.pdf; do
    issue="${pdf_filepath##pdf/}"
    issue="${issue%.pdf}"
    img_dir="images/$issue"

    # Skip if directory already exists
    if [ -d "$img_dir" ] && [ -n "$(ls -A1 "$img_dir" | grep -v '^\.DS_Store$')" ]; then
        echo "Skipping $pdf_filepath"
        continue
    fi

    echo "Processing $pdf_filepath..."
    mkdir -p "$img_dir"

    # Extract images preserving original encoding
    pdfimages -all "$pdf_filepath" "$img_dir/output"
    for f in "$img_dir"/*.*; do
      [ -e "$f" ] || continue
      mv "$f" "${f/output-/}";
    done 

    # 🔹 Always negate PNG images
    for f in "$img_dir"/*.png; do
        [ -e "$f" ] || continue
        magick "$f" -negate "$f"
    done

    # Convert PPM (lossless RGB) → JPG (good compression)
    for f in "$img_dir"/*.ppm; do
        [ -e "$f" ] || continue
        magick "$f" -quality 85 "${f%.ppm}.jpg"
        rm "$f"
    done
done

echo "Done."
