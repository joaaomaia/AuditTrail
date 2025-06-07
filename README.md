# 📊 AuditTrail

![logo](./imgs/social_preview_github.png)

AuditTrail é uma biblioteca para registrar e comparar snapshots de `pandas.DataFrame`. Ela auxilia no controle de qualidade e monitoramento de mudanças em pipelines de dados.

## Instalação

```bash
pip install -e .
```

## Exemplo de uso

```python
from audittrail import AuditTrail
import pandas as pd

df = pd.read_csv("meus_dados.csv")

trail = AuditTrail(track_histograms=True,
                   track_distributions=True,
                   enable_logging=True)

trail.take_snapshot(df, name="original")

# Após transformações...
df_filtrado = df.drop(columns=["coluna_irrelevante"])
trail.take_snapshot(df_filtrado, name="filtrado")

trail.compare_snapshots("original", "filtrado")
```

## Parâmetros da Classe

- `track_histograms` – armazena histogramas das colunas para análises futuras.
- `track_distributions` – calcula métricas de distribuição ao comparar snapshots.
- `enable_logging` – grava logs no arquivo `audit_trail.log`.
- `auto_detect_types` – identifica automaticamente colunas numéricas e categóricas.
- `target_col` – nome da coluna de alvo ignorada na detecção automática.
- `limite_categorico` – quantidade de valores únicos para considerar uma coluna categórica.
- `default_keys` – chaves padrão usadas na verificação de duplicatas.

## Métodos Disponíveis

- `take_snapshot(df, name, keys=None)` – salva estatísticas do DataFrame.
- `describe_snapshot(name)` – exibe informações detalhadas de um snapshot.
- `compare_snapshots(name1, name2)` – compara dois snapshots salvos.
- `list_snapshots()` – lista os snapshots armazenados.

## Métricas de Drift Suportadas

Quando `track_distributions=True`, são calculados:

- Teste Kolmogorov–Smirnov (KS).
- Population Stability Index (PSI).

## Requisitos

- Python 3.8 ou superior
- pandas
- numpy
- scipy
- ipython

## Licença

Distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.

## Autor

João Maia (maiaufrrj)
