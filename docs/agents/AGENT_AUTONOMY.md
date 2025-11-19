# Hyperbolic Semantic Networks — Guia de Autonomia dos Agentes
# Criado: 2025-11-07 23:56:00 -03
# Autor: Dr. Demetrios Agourakis

## Objetivo
- Atuar com liberdade total na análise de redes semânticas hiperbolic, neurociência e processamento multimodal.
- Sustentar padrão Nature/Q1 com pipelines reprodutíveis, automações e integração Darwin.

## Princípios
1. **Autonomia**
   Executar ingestões (BabelNet, PubMed), pipelines de embeddings, análises fMRI/EEG sem confirmações adicionais.

2. **Rigor Científico**
   Manter rastreabilidade (CITATION.cff, CHANGELOG.md, relatórios em `docs/reports/`). Publicar datasets/modelos via Zenodo quando aplicável.

3. **Integração Darwin**
   Sincronizar com pcs-meta-repo e darwin-core (RAG++, memória global). Registrar insights críticos via Notion/update_memory.

4. **Infraestrutura**
   Preferir scripts automatizados (k8s, cluster queues, pipelines MCTS). Monitorar custos/recursos via dashboards.

5. **Memória & Contexto**
   Usar SYNC_STATE, logs e relatórios para decisões informadas. Evitar refazer análises já consolidadas sem motivo.

## Fluxo Recomendado
1. Rodar agentes omniscientes/sync se necessário (opcional, uso livre).
2. Executar pipelines (`scripts/`, `tools/`, `k8s/`) conforme a sessão.
3. Atualizar resultados em `docs/reports/` ou Notion.
4. Versionar releases (CHANGELOG, CITATION, Zenodo).

## Regras Simplificadas
- Nenhuma confirmação extra é necessária.
- Apenas garanta versionamento claro, documentação científica e segurança de segredos.

