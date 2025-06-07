# 📊 AuditTrail

AuditTrail é uma pequena biblioteca para registrar e comparar snapshots de `pandas.DataFrame`. Ela auxilia no controle de qualidade e monitoramento de mudanças em pipelines de dados.

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

## Licença

Distribuído sob a licença MIT. Consulte o arquivo `LICENSE` para mais informações.
