# 📊 AuditTrail

**AuditTrail** é um utilitário leve para rastrear e comparar transformações em DataFrames `pandas`. Ele foi projetado para auditoria de dados, controle de qualidade e monitoramento de mudanças ao longo do tempo em pipelines de dados — ideal para aplicações como modelagem de risco de crédito, limpeza de dados e validação de pré-processamentos.

---

## 🚀 Principais Funcionalidades

- 📸 **Snapshots** de DataFrames com estatísticas e metadados
- 🔍 **Comparação entre snapshots** para detectar alterações
- 🧱 Detecção de **mudanças estruturais**: tipos, shape, valores ausentes, duplicatas
- 📊 Avaliação de **distribuições** com KS-test e PSI
- 🧠 Auto-detecção de colunas numéricas e categóricas
- 📝 Suporte a **logging automático**

---

## 🧩 Exemplo de Uso

```python
from utils import AuditTrail
import pandas as pd

df = pd.read_csv("meus_dados.csv")

audit = AuditTrail(track_histograms=True, track_distributions=True, enable_logging=True)

audit.take_snapshot(df, name="original")

# Após transformação
df_filtrado = df.drop(columns=["coluna_irrelevante"])
audit.take_snapshot(df_filtrado, name="filtrado")

# Comparação
audit.compare_snapshots("original", "filtrado")


⚙️ Parâmetros da Classe
Parâmetro	Descrição
track_histograms	Salva histogramas (valor absoluto) por coluna
track_distributions	Habilita comparação de distribuições via KS-test e PSI
enable_logging	Ativa logging em arquivo .log
auto_detect_types	Detecta colunas numéricas e categóricas automaticamente
target_col	Nome da coluna alvo a ser ignorada nas heurísticas
limite_categorico	Número máximo de valores únicos para uma coluna ser considerada categórica
default_keys	Lista de colunas-chave para checar duplicatas

📌 Métodos Disponíveis
take_snapshot(df, name): tira um snapshot do DataFrame atual

describe_snapshot(name): exibe resumo detalhado do snapshot

compare_snapshots(name1, name2): compara dois snapshots e destaca mudanças

list_snapshots(): lista todos os snapshots salvos

📈 Métricas de Drift Suportadas
KS-test: compara a forma das distribuições

PSI (Population Stability Index): detecta variações estatísticas relevantes (>0.2 sinaliza alerta)

🧪 Requisitos
pandas

numpy

scipy

📄 Licença
Este projeto está licenciado sob os termos da Licença MIT.

✍️ Autor
João Maia – github.com/joaaomaia