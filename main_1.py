import pandas as pd

# df = pd.read_csv("files\Principal_Commodity_wise_export_for_the_year_202223.csv")

# unique_values = df["PRINCIPLE COMMODITY"].unique()

# print(unique_values)

df = pd.read_excel("files/TradeStat-Meidb-Import-Commoditywise-all-countries (2).xlsx", skiprows=2)
top10 = df.nlargest(10, 'Jan-Dec2019                    (R)')[["Country", 'Jan-Dec2019                    (R)']]
print(top10)



