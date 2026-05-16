#!/bin/bash
# deploy_hf.sh — Push LexBridge to Hugging Face Spaces

set -e

# Configuration
HF_USER="${HF_USER:-$(git config user.name)}"
SPACE_NAME="${SPACE_NAME:-lexbridge}"
HF_REPO="https://huggingface.co/spaces/${HF_USER}/${SPACE_NAME}"

echo "🚀 Deploying LexBridge to Hugging Face Spaces..."
echo "   👤 User: ${HF_USER}"
echo "   🏠 Space: ${SPACE_NAME}"
echo "   🔗 Repo: ${HF_REPO}"
echo ""

# Check prerequisites
if ! command -v git &> /dev/null; then
    echo "❌ git is required but not installed"
    exit 1
fi

# Check if HF token is set (optional, git credential helper works too)
if [ -z "$HF_TOKEN" ]; then
    echo "⚠️ HF_TOKEN not set in environment"
    echo "   For smoother deploys, create a token at:"
    echo "   https://huggingface.co/settings/tokens"
    echo "   Then: export HF_TOKEN=hf_..."
    echo ""
    echo "Continuing with git credential prompt..."
fi

# Initialize git if needed
if [ ! -d ".git" ]; then
    echo "📦 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit: LexBridge legal aid agent"
fi

# Add or update HF remote
git remote remove hf 2>/dev/null || true
git remote add hf "${HF_REPO}"

# Push to HF Spaces
echo "📤 Pushing to Hugging Face Spaces..."
git push hf main

echo ""
echo "✅ Deployment initiated!"
echo ""
echo "🔗 Your live demo will be available at:"
echo "   https://huggingface.co/spaces/${HF_USER}/${SPACE_NAME}"
echo ""
echo "📝 Post-deployment steps:"
echo "   1. Go to your Space settings on Hugging Face"
echo "   2. Add GROQ_API_KEY to Repository Secrets"
echo "   3. Set Space SDK to 'Streamlit' if not already"
echo "   4. Wait ~2-3 minutes for build to complete"
echo "   5. Test with the 'Load Sample' button"
echo ""
echo "🔧 Troubleshooting:"
echo "   - Check 'App' tab in your Space for build logs"
echo "   - Ensure requirements.txt has all dependencies"
echo "   - Verify legal_kb.faiss is committed (small enough for HF)"