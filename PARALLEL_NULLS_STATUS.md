# 🚀 Análise de Nulls Estruturais - Status da Execução

**Data de início:** 2025-11-03 13:53  
**Modo:** Execução paralela local (8 processos Python)  
**Estimativa:** 2-4 horas

---

## ✅ Configuração

| Parâmetro | Valor |
|-----------|-------|
| Línguas | Spanish, English, Dutch, Chinese |
| Tipos de null | Configuration, Triadic |
| Total de jobs | 8 (rodando em paralelo) |
| Réplicas por job | M = 1000 |
| Alpha (idleness) | 0.5 |
| Seeds | 123-130 (único por job) |

---

## 📊 Status dos Jobs

| Job | Arquivo de entrada | Log | Status inicial |
|-----|-------------------|-----|----------------|
| spanish-configuration | spanish_edges.csv (13,150 edges) | `/tmp/structural_nulls_logs/spanish_configuration.log` | ✅ Iniciado |
| spanish-triadic | spanish_edges.csv | `/tmp/structural_nulls_logs/spanish_triadic.log` | ✅ Iniciado (κ_real=0.0536) |
| english-configuration | english_edges.csv (16,543 edges) | `/tmp/structural_nulls_logs/english_configuration.log` | ✅ Iniciado |
| english-triadic | english_edges.csv | `/tmp/structural_nulls_logs/english_triadic.log` | ✅ Iniciado (κ_real=0.1166) |
| dutch-configuration | dutch_edges.csv (19,160 edges) | `/tmp/structural_nulls_logs/dutch_configuration.log` | ✅ Iniciado (κ_real=0.1248) |
| dutch-triadic | dutch_edges.csv | `/tmp/structural_nulls_logs/dutch_triadic.log` | ✅ Iniciado (κ_real=0.1248) |
| chinese-configuration | chinese_edges.csv (10,838 edges) | `/tmp/structural_nulls_logs/chinese_configuration.log` | ✅ Iniciado |
| chinese-triadic | chinese_edges.csv | `/tmp/structural_nulls_logs/chinese_triadic.log` | ✅ Iniciado (κ_real=0.0007) |

---

## 📂 Arquivos de saída

Os resultados serão salvos em:

```
/home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls/
├── spanish_configuration_nulls.json
├── spanish_triadic_nulls.json
├── english_configuration_nulls.json
├── english_triadic_nulls.json
├── dutch_configuration_nulls.json
├── dutch_triadic_nulls.json
├── chinese_configuration_nulls.json
└── chinese_triadic_nulls.json
```

Cada arquivo JSON conterá:
- `language`: código da língua
- `null_type`: 'configuration' ou 'triadic'
- `M`: número de réplicas (1000)
- `kappa_real`: curvatura da rede real
- `kappa_null_mean`: média das curvaturas nulas
- `kappa_null_std`: desvio padrão
- **`delta_kappa`**: Δκ = κ_real - κ_null_mean
- **`p_MC`**: p-valor Monte Carlo (two-tailed)
- **`cliff_delta`**: Cliff's δ (effect size robusto)
- `ci_95_lower`, `ci_95_upper`: intervalo de confiança 95%
- `kappa_nulls`: array com todas as 1000 curvaturas nulas

---

## 🔍 Como monitorar

### Verificar processos ativos
```bash
ps aux | grep "07_structural_nulls_single_lang.py" | grep -v grep
```

### Ver logs em tempo real (todos)
```bash
tail -f /tmp/structural_nulls_logs/*.log
```

### Ver log de um job específico
```bash
tail -f /tmp/structural_nulls_logs/spanish_configuration.log
```

### Verificar arquivos de saída gerados
```bash
ls -lh /home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls/*.json
```

### Ver log master (script shell)
```bash
tail -f /tmp/parallel_nulls_master.log
```

---

## ⏱️ Estimativa de tempo

**Por tipo de null:**
- Configuration model: ~20-30 minutos por língua (~1.2s/réplica)
- Triadic-rewire: **2-3 horas por língua** (~10-12s/réplica)

**Total esperado:** ~2.5-4 horas para completar todos os 8 jobs em paralelo

**Fastest completion:** Configuration models completarão primeiro (~30 min)  
**Slowest completion:** Triadic models completarão por último (~3-4 horas)

---

## 📈 Próximos passos após conclusão

1. ✅ **Verificar resultados:**
   ```bash
   ls -lh /home/agourakis82/workspace/hyperbolic-semantic-networks/results/structural_nulls/
   ```

2. ✅ **Combinar resultados** (script já pronto):
   ```bash
   cd /home/agourakis82/workspace/hyperbolic-semantic-networks/code/analysis
   python combine_null_results.py  # (criar se necessário)
   ```

3. ✅ **Preencher placeholders no manuscrito:**
   ```bash
   python 08_fill_placeholders.py
   ```

4. ✅ **Gerar PDF final v1.8:**
   ```bash
   cd /home/agourakis82/workspace/hyperbolic-semantic-networks/manuscript
   pandoc main.md -o main.pdf --pdf-engine=xelatex
   ```

---

## 🚨 Troubleshooting

### Se algum processo falhar:

1. Verificar erro no log:
   ```bash
   tail -50 /tmp/structural_nulls_logs/<language>_<null_type>.log
   ```

2. Reexecutar job específico manualmente:
   ```bash
   cd /home/agourakis82/workspace/hyperbolic-semantic-networks/code/analysis
   python 07_structural_nulls_single_lang.py \
     --language spanish \
     --null-type configuration \
     --edge-file ../../data/processed/spanish_edges.csv \
     --output-dir ../../results/structural_nulls \
     --M 1000 --alpha 0.5 --seed 123
   ```

### Se quiser parar todos os processos:

```bash
pkill -f "07_structural_nulls_single_lang.py"
```

---

## 💾 Recursos usados

**CPU:** 8 cores (1 por job)  
**RAM:** ~8-16 GB por processo (estimado)  
**Disco:** Logs em `/tmp/`, resultados ~10-20 MB total  

**Nota:** Os processos estão rodando com `nice` level normal. Se necessário, ajustar prioridade:
```bash
renice -n 10 -p <PID>  # Reduzir prioridade (liberar recursos)
```

---

**Status atualizado automaticamente pelo script master:** `/tmp/parallel_nulls_master.log`



