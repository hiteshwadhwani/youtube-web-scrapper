import pandas as pd
df = pd.read_json("./files/Krish_naik.json")
for i in df.values.tolist():
    print(i[0])