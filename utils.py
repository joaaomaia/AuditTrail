import pandas as pd
import numpy as np
import warnings
from typing import Optional, List, Tuple
from scipy.stats import ks_2samp
from IPython.display import display
import logging

pd.set_option("display.max_columns", None)     # mostra todas as colunas
pd.set_option("display.max_rows", 100)         # mostra até 100 linhas
pd.set_option("display.width", 1000)           # define largura máxima
pd.set_option("display.colheader_justify", "center")  # centraliza cabeçalhos


class AuditTrail:
    def __init__(
        self,
        track_histograms: bool = False,
        track_distributions: bool = False,
        enable_logging: bool = False,
        auto_detect_types: bool = False,
        target_col: str = 'target',
        limite_categorico: int = 50,
        default_keys: Optional[List[str]] = None,  # NOVO
    ):
        self.track_histograms = track_histograms
        self.track_distributions = track_distributions
        self.enable_logging = enable_logging
        self.auto_detect_types = auto_detect_types
        self.target_col = target_col
        self.limite_categorico = limite_categorico
        self.default_keys = default_keys           # NOVO
        self.snapshots = {}

        if self.enable_logging:
            logging.basicConfig(
                filename="audit_trail.log",
                level=logging.INFO,
                format="%(asctime)s | %(levelname)s | %(message)s",
            )


    def take_snapshot(self, df: pd.DataFrame, name: str, keys: Optional[List[str]] = None):
        if name in self.snapshots:
            raise ValueError(f"Snapshot com nome '{name}' já existe.")

        keys = keys or self.default_keys  # ← aplica default_keys se nada for passado

        snap = {
            'shape': df.shape,
            'dtypes': df.dtypes.astype(str),
            'missing': df.isna().sum(),
            'num_summary': df.describe(include=[np.number]).T,
            'cat_summary': df.describe(include=['object', 'category']).T,
            'key_dupes': df.duplicated(subset=keys).sum() if keys else None,
            'keys': keys,
        }

        if self.track_histograms:
            snap['histograms'] = {
                col: df[col].value_counts(dropna=False).to_dict()
                for col in df.columns
                if df[col].dtype.kind in {'O', 'i', 'u', 'f', 'b'}
            }

        if self.auto_detect_types:
            num_cols, cat_cols = self._search_dtypes(df)
            snap['num_cols'] = num_cols
            snap['cat_cols'] = cat_cols

        self.snapshots[name] = snap
        self._log(f"Snapshot '{name}' salvo com sucesso. Shape: {df.shape}")


    def describe_snapshot(self, name: str):
        if name not in self.snapshots:
            raise ValueError(f"Snapshot '{name}' não encontrado.")

        snap = self.snapshots[name]
        print(f"\n📄 Descrição do snapshot '{name}':\n")

        print(f"▶️ Shape: {snap['shape']}")
        print(f"▶️ Chaves de duplicação: {snap['keys']}")
        if snap['keys']:
            print(f"   • Duplicatas nas chaves: {snap['key_dupes']}")

        print("\n🧱 Tipos de dados:")
        display(snap['dtypes'])

        # Mostra lista de colunas numéricas e categóricas (se autodetectadas)
        if self.auto_detect_types:
            print("\n🔎 Colunas detectadas automaticamente:")
            print(f"   • Numéricas ({len(snap.get('num_cols', []))}): {snap.get('num_cols', [])}")
            print(f"   • Categóricas ({len(snap.get('cat_cols', []))}): {snap.get('cat_cols', [])}")

        print("\n🕳️ Valores ausentes:")
        missing = snap['missing']
        missing = missing[missing > 0]
        if missing.empty:
            print("  ✅ Nenhuma coluna com valores ausentes.")
        else:
            display(missing.sort_values(ascending=False))

        print("\n📊 Estatísticas numéricas:")
        display(snap['num_summary'])

        print("\n🏷️ Estatísticas categóricas:")
        display(snap['cat_summary'])

        if self.track_histograms and 'histograms' in snap:
            print("\n📈 Histogramas (categorias apenas):")
            for col in snap.get('cat_cols', []):
                hist = snap['histograms'].get(col)
                if hist:
                    top3 = dict(list(hist.items())[:3])
                    print(f"  {col}: {len(hist)} valores distintos (top 3: {top3})")



    def compare_snapshots(self, name1: str, name2: str):
        if name1 not in self.snapshots or name2 not in self.snapshots:
            raise ValueError("Snapshot não encontrado.")

        snap1, snap2 = self.snapshots[name1], self.snapshots[name2]

        print(f"\n🔍 Comparando '{name1}' vs '{name2}':\n")
        print("▶️ Shape:")
        print(f"  {name1}: {snap1['shape']} vs {name2}: {snap2['shape']}\n")

        common_cols = snap1['dtypes'].index.intersection(snap2['dtypes'].index)
        dtypes_diff = (snap1['dtypes'][common_cols] != snap2['dtypes'][common_cols])
        dtypes_diff = dtypes_diff.loc[lambda x: x]

        if not dtypes_diff.empty:
            print("▶️ Mudanças em tipos de dados:\n", dtypes_diff, "\n")

        missing_diff = (snap2['missing'] - snap1['missing']).loc[lambda x: x != 0]
        if not missing_diff.empty:
            print("▶️ Diferença de valores ausentes:\n", missing_diff, "\n")

        if snap1['keys'] and snap2['keys']:
            print("▶️ Duplicatas nas chaves:")
            print(f"  {name1}: {snap1['key_dupes']} vs {name2}: {snap2['key_dupes']}\n")

        print("▶️ Mudança na média de variáveis numéricas:")
        mean_diff = (snap2['num_summary']['mean'] - snap1['num_summary']['mean']).dropna()
        print(mean_diff[mean_diff.abs() > 1e-6])

        if self.track_distributions and 'histograms' in snap1 and 'histograms' in snap2:
            print("\n▶️ KS-test e PSI para variáveis:")
            cols_common = set(snap1.get('histograms', {})).intersection(snap2.get('histograms', {}))
            for col in sorted(cols_common):
                dist1 = snap1['histograms'].get(col, {})
                dist2 = snap2['histograms'].get(col, {})

                ks_stat = self._calculate_ks(dist1, dist2)
                psi_val = self._calculate_psi(dist1, dist2)

                alerta = " ⚠️" if psi_val > 0.2 else ""
                print(f"  {col}: KS={ks_stat:.3f}, PSI={psi_val:.3f}{alerta}")

                if psi_val > 0.2:
                    self._log(f"Alerta PSI>0.2 detectado para '{col}': PSI={psi_val:.3f}")

    def _calculate_ks(self, dist1: dict, dist2: dict):
        v1 = list(dist1.values())
        v2 = list(dist2.values())
        if len(v1) > 1 and len(v2) > 1:
            return ks_2samp(v1, v2).statistic
        return 0.0

    def _calculate_psi(self, expected: dict, actual: dict, epsilon=1e-6):
        keys = set(expected.keys()).union(actual.keys())
        total_expected = sum(expected.values()) + epsilon
        total_actual = sum(actual.values()) + epsilon
        psi = 0.0
        for k in keys:
            e = expected.get(k, 0) / total_expected
            a = actual.get(k, 0) / total_actual
            if e > 0:
                psi += (e - a) * np.log((e + epsilon) / (a + epsilon))
        return round(psi, 4)

    def _search_dtypes(self, df: pd.DataFrame) -> Tuple[List[str], List[str]]:
        force_categorical = []
        id_patterns = ['client_id', '_id', 'id_', 'codigo', 'key']
        remove_ids = True
        verbose = False

        num_cols, cat_cols = [], []
        for col in df.columns:
            if col == self.target_col:
                continue
            s = df[col]
            if s.isnull().mean() > 0.9:
                continue
            if pd.api.types.is_numeric_dtype(s):
                if remove_ids and any(p in col.lower() for p in id_patterns):
                    continue
                num_cols.append(col)
            elif s.dtype == 'object' or pd.api.types.is_string_dtype(s):
                if remove_ids and any(p in col.lower() for p in id_patterns):
                    continue
                if s.nunique(dropna=True) <= self.limite_categorico:
                    cat_cols.append(col)
            elif pd.api.types.is_bool_dtype(s):
                cat_cols.append(col)
        return num_cols, cat_cols

    def _log(self, msg):
        if self.enable_logging:
            logging.info(msg)

    def list_snapshots(self):
        print("📚 Snapshots disponíveis:")
        for k in self.snapshots:
            print(f" - {k}")
