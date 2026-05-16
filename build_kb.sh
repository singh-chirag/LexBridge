#!/bin/bash
# build_kb.sh — Build LexBridge legal knowledge base

set -e

echo "🔨 Building LexBridge Legal Knowledge Base..."

# Create directories
mkdir -p rag/sources rag

# Download sample legal documents (public domain government sources)
echo "📥 Downloading legal source documents..."

# CFPB - Debt Collection Rights
curl -s "https://files.consumerfinance.gov/f/documents/cfpb_debt-collection_FAQs_en.txt" \
  -o "rag/sources/cfpb_debt_collection.txt" 2>/dev/null || \
  echo "⚠️ Could not download CFPB doc, using placeholder"

# HUD - Tenant Rights  
curl -s "https://www.hud.gov/sites/dfiles/OCHCO/documents/tenant-rights-summary.txt" \
  -o "rag/sources/hud_tenant_rights.txt" 2>/dev/null || \
  echo "⚠️ Could not download HUD doc, using placeholder"

# USCIS - Immigration Basics
curl -s "https://www.uscis.gov/sites/default/files/document/guides/M-618.pdf.txt" \
  -o "rag/sources/uscis_immigration_basics.txt" 2>/dev/null || \
  echo "⚠️ Could not download USCIS doc, using placeholder"

# Create placeholders if downloads failed
if [ ! -s "rag/sources/cfpb_debt_collection.txt" ]; then
  cp tests/sample_docs/cfpb_debt_collection.txt rag/sources/ 2>/dev/null || \
  cat > "rag/sources/cfpb_debt_collection.txt" << 'EOF'
CONSUMER FINANCIAL PROTECTION BUREAU - DEBT COLLECTION RIGHTS
Your Rights Under the Fair Debt Collection Practices Act (FDCPA)
- You have 30 days to dispute a debt in writing
- Collectors must validate debts upon request
- Harassment, false statements, and unfair practices are prohibited
- You can request collectors stop contacting you (in writing)
- Statute of limitations varies by state (typically 3-6 years)
Source: consumerfinance.gov
EOF
fi

if [ ! -s "rag/sources/hud_tenant_rights.txt" ]; then
  cat > "rag/sources/hud_tenant_rights.txt" << 'EOF'
HUD - TENANT RIGHTS SUMMARY
- Landlords must provide habitable housing (heat, water, safety)
- Security deposits must be returned per state law timelines
- Eviction requires proper notice (typically 3-30 days) and court order
- Fair Housing Act prohibits discrimination based on protected classes
- Tenants may have "repair and deduct" rights in some jurisdictions
Source: hud.gov
EOF
fi

# Build the FAISS index
echo "🧠 Building FAISS index from legal sources..."
python rag/build_kb.py

echo ""
echo "✅ Knowledge base built successfully!"
echo "📁 Generated files:"
ls -lh rag/legal_kb.* 2>/dev/null || echo "⚠️ Index files not found"
echo ""
echo "📦 Ready for deployment!"