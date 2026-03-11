from db_connector import *

df = fn_read_data_cloud("bronze", "bist_daily_high_filtered")

print(df.head())