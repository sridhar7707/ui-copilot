#!/bin/bash
# Rename map: ChatGPT-generated filenames -> data/benchmarks/images/{quality}/{category}/{id}.png
#
# Usage:
#   1. Save all 61 downloaded PNGs into one folder, e.g. ~/Downloads/uicopilot_benchmarks/
#   2. Copy this script into that folder (or adjust SRC_DIR below)
#   3. Run: bash rename_benchmark_images.sh
#   4. It copies + renames into the correct data/benchmarks/images/ tree, ready to
#      sit next to the matching .json files
#
# NOTE: excellent_table_04.png and excellent_metrics_02.png do not exist yet —
# this script does not reference them. Generate those two separately, name them
# to match (excellent_table_04.png, excellent_metrics_02.png), and drop them in
# data/benchmarks/images/excellent/tables/ and .../metrics/ respectively.

set -e

SRC_DIR="${1:-.}"
DEST_ROOT="data/benchmarks/images"

declare -A MAP=(
  # ---- EXCELLENT ----
  [excellent_dashboard_01.png]="excellent/dashboards/dashboard_001.png"
  [excellent_dashboard_02.png]="excellent/dashboards/dashboard_002.png"
  [excellent_dashboard_03.png]="excellent/dashboards/dashboard_003.png"
  [excellent_dashboard_04.png]="excellent/dashboards/dashboard_004.png"
  [excellent_dashboard_05.png]="excellent/dashboards/dashboard_005.png"
  [excellent_dashboard_06.png]="excellent/dashboards/dashboard_006.png"
  [excellent_dashboard_07.png]="excellent/dashboards/dashboard_007.png"
  [excellent_dashboard_08.png]="excellent/dashboards/dashboard_008.png"

  [excellent_cards_01.png]="excellent/cards/cards_001.png"
  [excellent_cards_02.png]="excellent/cards/cards_002.png"
  [excellent_cards_03.png]="excellent/cards/cards_003.png"
  [excellent_cards_04.png]="excellent/cards/cards_004.png"

  [excellent_table_01.png]="excellent/tables/tables_001.png"
  [excellent_table_02.png]="excellent/tables/tables_002.png"
  [excellent_table_03.png]="excellent/tables/tables_003.png"
  # excellent_table_04.png — MISSING, generate separately

  [excellent_form_01.png]="excellent/forms/forms_001.png"
  [excellent_form_02.png]="excellent/forms/forms_002.png"
  [excellent_form_03.png]="excellent/forms/forms_003.png"
  [excellent_form_04.png]="excellent/forms/forms_004.png"

  [excellent_nav_01.png]="excellent/navigation/navigation_001.png"
  [excellent_nav_02.png]="excellent/navigation/navigation_002.png"
  [excellent_nav_03.png]="excellent/navigation/navigation_003.png"
  [excellent_nav_04.png]="excellent/navigation/navigation_004.png"

  [excellent_chart_01.png]="excellent/charts/charts_001.png"
  [excellent_chart_02.png]="excellent/charts/charts_002.png"
  [excellent_chart_03.png]="excellent/charts/charts_003.png"
  [excellent_chart_04.png]="excellent/charts/charts_004.png"

  [excellent_metrics_01.png]="excellent/metrics/metrics_001.png"
  # excellent_metrics_02.png — MISSING, generate separately
  [excellent_metrics_03.png]="excellent/metrics/metrics_003.png"
  [excellent_metrics_04.png]="excellent/metrics/metrics_004.png"

  # ---- POOR ----
  [poor_dashboard_01.png]="poor/dashboards/dashboard_001.png"
  [poor_dashboard_02.png]="poor/dashboards/dashboard_002.png"
  [poor_dashboard_03.png]="poor/dashboards/dashboard_003.png"
  [poor_dashboard_04.png]="poor/dashboards/dashboard_004.png"
  [poor_dashboard_05.png]="poor/dashboards/dashboard_005.png"
  [poor_dashboard_06.png]="poor/dashboards/dashboard_006.png"
  [poor_dashboard_07.png]="poor/dashboards/dashboard_007.png"
  [poor_dashboard_08.png]="poor/dashboards/dashboard_008.png"

  [poor_cards_01.png]="poor/cards/cards_001.png"
  [poor_cards_02.png]="poor/cards/cards_002.png"
  [poor_cards_03.png]="poor/cards/cards_003.png"
  [poor_cards_04.png]="poor/cards/cards_004.png"

  [poor_table_01.png]="poor/tables/tables_001.png"
  [poor_table_02.png]="poor/tables/tables_002.png"
  [poor_table_03.png]="poor/tables/tables_003.png"
  [poor_table_04.png]="poor/tables/tables_004.png"

  [poor_form_01.png]="poor/forms/forms_001.png"
  [poor_form_02.png]="poor/forms/forms_002.png"
  [poor_form_03.png]="poor/forms/forms_003.png"
  [poor_form_04.png]="poor/forms/forms_004.png"

  [poor_nav_01.png]="poor/navigation/navigation_001.png"
  [poor_nav_02.png]="poor/navigation/navigation_002.png"
  [poor_nav_03.png]="poor/navigation/navigation_003.png"
  [poor_nav_04.png]="poor/navigation/navigation_004.png"

  [poor_chart_01.png]="poor/charts/charts_001.png"
  [poor_chart_02.png]="poor/charts/charts_002.png"
  [poor_chart_03.png]="poor/charts/charts_003.png"
  [poor_chart_04.png]="poor/charts/charts_004.png"

  [poor_metrics_01.png]="poor/metrics/metrics_001.png"
  [poor_metrics_02.png]="poor/metrics/metrics_002.png"
  [poor_metrics_03.png]="poor/metrics/metrics_003.png"
  [poor_metrics_04.png]="poor/metrics/metrics_004.png"
)

copied=0
missing=0

for src in "${!MAP[@]}"; do
  dest="${MAP[$src]}"
  dest_path="$DEST_ROOT/$dest"
  mkdir -p "$(dirname "$dest_path")"
  if [ -f "$SRC_DIR/$src" ]; then
    cp "$SRC_DIR/$src" "$dest_path"
    echo "OK    $src -> $dest_path"
    copied=$((copied + 1))
  else
    echo "MISS  $src not found in $SRC_DIR"
    missing=$((missing + 1))
  fi
done

echo ""
echo "Copied: $copied   Missing: $missing"
echo "Remember: excellent_table_04.png and excellent_metrics_02.png are not"
echo "in the ChatGPT batch — generate those two separately to complete Pack 1."
