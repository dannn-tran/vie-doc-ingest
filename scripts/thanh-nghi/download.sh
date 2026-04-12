#!/bin/bash
base_url="https://www.namkyluctinh.org/eBooks/Tap%20Chi/Thanh%20Nghi"

mkdir -p pdf
cd pdf

for i in $(seq -w 1 120)
do
    filename="${i}.pdf"
    url="${base_url}/${filename}"
    if [ -f "$filename" ]; then
        echo "Skipping $filename (already exists)"
    else
        echo "Downloading $url"
        curl -O "$url"
    fi
done
