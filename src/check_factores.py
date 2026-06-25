# src/check_factores.py
import pickle

with open("data/processed/factores_inflacion_trim.pkl", "rb") as f:
    factores = pickle.load(f)

print("Factores de deflacion (IPC_periodo / IPC_base):")
print("Base = 2026-T2 (IPC_GBA ≈ 11465.55, IPC_Cuyo ≈ 11630.60)")
print("-" * 60)
print(f"{'Año-T':<10} {'GBA':<12} {'Cuyo':<12}")
print("-" * 60)
for (ano, trim), v in sorted(factores.items()):
    print(f"{ano}-T{trim:<2}   {v['gba']:.6f}   {v['cuyo']:.6f}")