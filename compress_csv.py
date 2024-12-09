import pandas as pd
import numpy as np
from dateutil.parser import parse

# df = pd.read_csv("data/dionaea_log_compress.csv")
# column_to_int = ["protocol", "type", "transport"]
# column_to_datetime = ["date", "timestamp"]

# for col in column_to_int:
#     df[col] = df[col].astype(int)

# for col in column_to_datetime:
#     df[col] = df[col].apply(lambda x: parse(x))

# for col in df.select_dtypes(include=[np.int64]):
#     df[col] = pd.to_numeric(df[col], downcast="signed")

# print(df.info())
# df.to_csv("data/dionaea_log_compress.csv", index=False)

df = pd.read_csv("data/dionaea_log_category.csv")
print(df["type"].value_counts())