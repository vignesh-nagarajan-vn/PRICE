#!/bin/bash
# Download public HMDA home-purchase applications (originated, or approved but not accepted) from the CFPB
# HMDA Data Browser API.  Usage: bash code/download_hmda.sh   (run from the project folder)
set -u
OUT="data/raw"
for y in 2022 2023; do
  for s in CA TX FL; do
    f="$OUT/hmda_${s}_${y}_purchase.csv"
    if [ -s "$f" ]; then echo "exists: $f"; continue; fi
    for attempt in 1 2 3; do
      curl -sS -L --compressed --max-time 1800 -o "$f.part" \
        "https://ffiec.cfpb.gov/v2/data-browser-api/view/csv?states=${s}&years=${y}&actions_taken=1,2&loan_purposes=1"
      if [ -s "$f.part" ] && head -c 200 "$f.part" | grep -q "action_taken"; then mv "$f.part" "$f"; break; fi
      echo "retry $attempt for $f"; rm -f "$f.part"; sleep 20
    done
    echo "$f: $(wc -l < "$f" 2>/dev/null) lines, $(du -h "$f" 2>/dev/null | cut -f1)"
  done
done
