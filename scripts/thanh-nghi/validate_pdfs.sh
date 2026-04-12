#!/usr/bin/env bash
# check_pdfs.sh — Validate PDF files in /pdf directory (macOS)
# Usage: ./check_pdfs.sh [-r]
#   -r   Remove invalid PDF files after reporting

PDF_DIR="pdf"
REMOVE=false

# Parse flags
while getopts ":r" opt; do
  case $opt in
    r) REMOVE=true ;;
    \?) echo "Unknown flag: -$OPTARG"; echo "Usage: $0 [-r]"; exit 1 ;;
  esac
done

# Ensure qpdf is available (install via: brew install qpdf)
if ! command -v qpdf &>/dev/null; then
  echo "Error: 'qpdf' is required but not installed."
  echo "Install it with: brew install qpdf"
  exit 1
fi

# Check directory exists
if [[ ! -d "$PDF_DIR" ]]; then
  echo "Error: Directory '$PDF_DIR' does not exist."
  exit 1
fi

# Counters
total=0
valid=0
invalid=0
removed=0

declare -a invalid_files=()

echo "========================================"
echo "  PDF Validation Summary — $PDF_DIR"
echo "========================================"

# Find all .pdf files (case-insensitive)
while IFS= read -r -d '' file; do
  total=$((total + 1))
  filename=$(basename "$file")

  # qpdf --check returns exit code 0 if the PDF is valid
  result=$(qpdf --check "$file" 2>&1)
  exit_code=$?

  if [[ $exit_code -eq 0 ]]; then
    valid=$((valid + 1))
    echo "  ✓  $filename"
  else
    invalid=$((invalid + 1))
    # Extract a short reason from qpdf output (first warning/error line)
    reason=$(echo "$result" | grep -Ei "error|warning|damaged|invalid" | head -1 | sed 's/^[[:space:]]*//')
    [[ -z "$reason" ]] && reason="qpdf reported an issue (exit code $exit_code)"
    echo "  ✗  $filename"
    echo "       Reason: $reason"
    invalid_files+=("$file")
  fi

done < <(find "$PDF_DIR" -maxdepth 1 -iname "*.pdf" -print0 | sort -z)

echo "========================================"
echo "  Total   : $total"
echo "  Valid   : $valid"
echo "  Invalid : $invalid"
echo "========================================"

# Remove invalid files if -r flag was set
if [[ "$REMOVE" == true && $invalid -gt 0 ]]; then
  echo ""
  echo "Removing invalid files..."
  for f in "${invalid_files[@]}"; do
    rm "$f" && removed=$((removed + 1)) && echo "  Deleted: $(basename "$f")"
  done
  echo ""
  echo "$removed invalid file(s) removed."
elif [[ "$REMOVE" == false && $invalid -gt 0 ]]; then
  echo ""
  echo "Run with -r to delete invalid files."
fi
