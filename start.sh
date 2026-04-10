#!/bin/bash
# GAIA Launch Script — starts both the Python backend and Vite frontend
# Usage: bash start.sh

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}⬡ GAIA Starting...${NC}"
echo ""

# Check Python
if ! command -v python &> /dev/null; then
    echo -e "${YELLOW}ERROR: Python not found. Install Python 3.11+${NC}"
    exit 1
fi

# Check Node
if ! command -v npm &> /dev/null; then
    echo -e "${YELLOW}ERROR: Node.js not found. Install Node.js 18+${NC}"
    exit 1
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}WARNING: Ollama not found. Install from https://ollama.com/download${NC}"
else
    echo -e "${BLUE}▶ Starting Ollama...${NC}"
    ollama serve &>/dev/null &
    sleep 1
fi

# Start Python backend
echo -e "${BLUE}▶ Starting GAIA backend (port 8008)...${NC}"
python core/server.py &
BACKEND_PID=$!
echo -e "  Backend PID: ${BACKEND_PID}"
sleep 2

# Start Vite frontend
echo -e "${BLUE}▶ Starting GAIA frontend (Vite)...${NC}"
npm run dev &
FRONTEND_PID=$!
echo -e "  Frontend PID: ${FRONTEND_PID}"

echo ""
echo -e "${GREEN}✅ GAIA is running!${NC}"
echo -e "  Frontend: ${BLUE}http://localhost:5173${NC}"
echo -e "  Backend:  ${BLUE}http://127.0.0.1:8008${NC}"
echo -e "  Status:   ${BLUE}http://127.0.0.1:8008/status${NC}"
echo ""
echo -e "Press ${YELLOW}Ctrl+C${NC} to stop everything."

# Trap Ctrl+C and kill both processes
trap "echo ''; echo -e '${YELLOW}Shutting down GAIA...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT

# Wait
wait
