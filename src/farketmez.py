from db_connector import *

df = fn_read_data_cloud("silver", "bist_daily_high_filtered")

print(df.head())