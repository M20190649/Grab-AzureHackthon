import glob
import pandas as pd

df_list = []
for file in glob.glob("dataset/part-*.parquet"):
    df_ = pd.read_parquet(file, engine = 'pyarrow')
    df_list.append(df_)

df = pd.concat(df_list, ignore_index=True)
df.shape