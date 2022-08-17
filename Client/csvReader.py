import pandas as pd


def read_parse_csv(filename):
    print(f"Lettura di '{filename}'...")
    with open(filename, "r") as f:
        df = pd.read_csv(f,sep=',',dtype='unicode')
        dataDict = df.to_dict("records")
        print("Lettura del file CSV completata")
        return dataDict
