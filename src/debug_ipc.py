import pandas as pd

df = pd.read_excel("data/external/sh_ipc_06_26.xls", sheet_name="Índices IPC Cobertura Nacional", header=None)
print(df.iloc[0:30, 0:3].to_string())