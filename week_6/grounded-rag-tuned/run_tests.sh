#!/bin/bash
# ============================================
# ТЕСТИРОВАНИЕ: grounded-rag-tuned
# Автотест всех конфигов local LLM
# ============================================

cd "$(dirname "$0")"

RESULTS_FILE="test_results.txt"
> "$RESULTS_FILE"

echo "========================================"
echo "Тестирование: grounded-rag-tuned"
echo "========================================"
echo ""

for CONFIG in fast balanced strict; do
    echo ">>> Тест: $CONFIG"
    echo "--- $CONFIG ---" >> "$RESULTS_FILE"
    
    LLM_CONFIG="$CONFIG" LLM_MODE=local ./venv/bin/python main.py --eval-only 2>&1 | tee -a "$RESULTS_FILE"
    
    echo "" >> "$RESULTS_FILE"
    echo "========================================"
    echo ""
done

echo ""
echo "========================================"
echo "РЕЗУЛЬТАТЫ СОХРАНЕНЫ: $RESULTS_FILE"
echo "========================================"

echo ""
echo "=== ИТОГОВАЯ ТАБЛИЦА ==="
printf "%-12s | %-10s | %-10s | %-8s | %s\n" "Config" "Fallback" "Sources" "Quotes" "Latency"
printf "%-12s | %-10s | %-10s | %-8s | %s\n" "------------" "----------" "----------" "--------" "-------"

for CONFIG in fast balanced strict; do
    FALL=$(grep "__CONFIG__:$CONFIG" -A 1 "$RESULTS_FILE" | grep "__FALLBACK__" | cut -d: -f2)
    SOUR=$(grep "__CONFIG__:$CONFIG" -A 2 "$RESULTS_FILE" | grep "__SOURCES__" | cut -d: -f2)
    QUOT=$(grep "__CONFIG__:$CONFIG" -A 3 "$RESULTS_FILE" | grep "__QUOTES__" | cut -d: -f2)
    LAT=$(grep "__CONFIG__:$CONFIG" -A 4 "$RESULTS_FILE" | grep "__LATENCY__" | cut -d: -f2)
    
    if [ -n "$FALL" ]; then
        printf "%-12s | %-10s | %-10s | %-8s | %s\n" "$CONFIG" "${FALL}%" "${SOUR}%" "${QUOT}%" "${LAT}s"
    fi
done
