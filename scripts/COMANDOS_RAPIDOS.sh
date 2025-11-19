#!/bin/bash
# Comandos Rápidos para Push GitHub + Zenodo
# Execute cada seção separadamente

echo "=========================================="
echo "REPOSITÓRIO: hyperbolic-semantic-networks"
echo "=========================================="
echo ""

# ============================================
# PASSO 1: Verificar pré-requisitos
# ============================================
echo "📋 PRÉ-REQUISITOS:"
echo ""
echo "1. Criar repo no GitHub (web):"
echo "   https://github.com/new"
echo "   Name: hyperbolic-semantic-networks"
echo "   Public, NO initialize"
echo ""
echo "Pressione ENTER quando repo criado no GitHub..."
read

# ============================================
# PASSO 2: Push para GitHub
# ============================================
echo ""
echo "🚀 PASSO 2: Push para GitHub"
echo ""

cd /home/agourakis82/workspace/hyperbolic-semantic-networks

# Add remote
git remote add origin https://github.com/agourakis82/hyperbolic-semantic-networks.git

# Push main
echo "Pushing main branch..."
git push -u origin main

# Push tags
echo "Pushing tags..."
git push origin --tags

echo ""
echo "✅ Push completo!"
echo "Verificar em: https://github.com/agourakis82/hyperbolic-semantic-networks"
echo ""
echo "Pressione ENTER para continuar com Zenodo..."
read

# ============================================
# PASSO 3: Enable Zenodo
# ============================================
echo ""
echo "🔗 PASSO 3: Zenodo Integration"
echo ""
echo "1. Abrir: https://zenodo.org/account/settings/github/"
echo "2. Login com GitHub"
echo "3. Encontrar: agourakis82/hyperbolic-semantic-networks"
echo "4. Toggle ON (verde)"
echo ""
echo "Pressione ENTER quando Zenodo habilitado..."
read

# ============================================
# PASSO 4: Test Release
# ============================================
echo ""
echo "🧪 PASSO 4: Test Release"
echo ""

# Create test tag
git tag v0.1.0-test -m "Test Zenodo integration"
git push origin v0.1.0-test

echo ""
echo "✅ Test tag pushed!"
echo ""
echo "⏳ AGUARDE 10 MINUTOS"
echo ""
echo "Depois verificar:"
echo "https://zenodo.org/search?q=hyperbolic-semantic-networks"
echo ""
echo "Se DOI aparecer → SUCCESS!"
echo ""
echo "Pressione ENTER quando DOI test obtido..."
read

# ============================================
# PASSO 5: Official Release
# ============================================
echo ""
echo "🎉 PASSO 5: Official Release"
echo ""

# Delete test tag
git tag -d v0.1.0-test
git push origin :refs/tags/v0.1.0-test

echo "✅ Test tag removida"
echo ""

# Push official v1.0.0
git push origin v1.0.0

echo ""
echo "✅ v1.0.0 released!"
echo ""
echo "⏳ Aguarde 10 min para DOI oficial"
echo "Verificar: https://zenodo.org/search?q=hyperbolic-semantic-networks"
echo ""
echo "=========================================="
echo "✅ PROCESSO COMPLETO!"
echo "=========================================="
echo ""
echo "NEXT STEPS:"
echo "1. Copiar DOI quando aparecer"
echo "2. Atualizar README.md com DOI"
echo "3. Atualizar CITATION.cff com DOI"
echo "4. Commit + push updates"
echo ""
echo "🎯 PAPER PRONTO PARA SUBMISSION!"

