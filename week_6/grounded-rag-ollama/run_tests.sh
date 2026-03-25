#!/bin/bash
# ============================================
# ТЕСТИРОВАНИЕ grounded-rag-ollama
# ============================================

cd "$(dirname "$0")"

# 1. Очистка старых логов
rm -f logs/llm_*.log

# 2. Cloud режим
echo ""
echo "=== CLOUD MODE ==="
LLM_MODE=cloud ./venv/bin/python main.py << 'EOF'
eval
exit
EOF

# 3. Local режим
echo ""
echo "=== LOCAL MODE ==="
LLM_MODE=local ./venv/bin/python main.py << 'EOF'
eval
exit
EOF

# 4. Сравнение latency
echo ""
echo "=== COMPARISON ==="
echo ""
echo "Cloud avg latency:"
if [ -f logs/llm_cloud.log ]; then
  cat logs/llm_cloud.log | python3 -c "import sys,json; d=[float(l['latency']) for l in [json.loads(x) for x in sys.stdin]]; print(f'  {sum(d)/len(d):.2f}s (n={len(d)})')"
else
  echo "  N/A"
fi

echo ""
echo "Local avg latency:"
if [ -f logs/llm_local.log ]; then
  cat logs/llm_local.log | python3 -c "import sys,json; d=[float(l['latency']) for l in [json.loads(x) for x in sys.stdin]]; print(f'  {sum(d)/len(d):.2f}s (n={len(d)})')"
else
  echo "  N/A"
fi

echo ""
echo "=== DONE ==="
