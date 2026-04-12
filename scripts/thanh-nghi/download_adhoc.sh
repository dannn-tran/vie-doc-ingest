#!/bin/bash

mkdir -p pdf

curl -L -O --output-dir "pdf" "https://www.namkyluctinh.org/eBooks/Tap%20Chi/Thanh%20Nghi/029-031.pdf"
curl -L -O --output-dir "pdf" "https://www.namkyluctinh.org/eBooks/Tap%20Chi/Thanh%20Nghi/051-054.pdf"
curl -L -O --output-dir "pdf" "https://www.namkyluctinh.org/eBooks/Tap%20Chi/Thanh%20Nghi/100-104.pdf"

echo "Done! Files saved to ./pdf/"

