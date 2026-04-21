#!/bin/bash
# Setup script for Ollama AI service

echo "🤖 Setting up Ollama AI for The Signal..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "📥 Installing Ollama..."
    curl -fsSL https://ollama.ai/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Start Ollama service
echo "🚀 Starting Ollama service..."
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama service already running"
else
    ollama serve &
    sleep 3
fi

# Pull lightweight models for CPU inference
echo "📦 Pulling AI models..."
echo "  - phi3 (3.8GB, lightweight, fast on CPU)"
ollama pull phi3

echo ""
echo "✅ Ollama setup complete!"
echo ""
echo "Available models:"
ollama list
echo ""
echo "To test: ollama run phi3 'Summarize wireless technology trends'"
