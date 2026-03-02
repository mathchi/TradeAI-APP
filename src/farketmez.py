from db_connector import *

df = fn_read_data_cloud("test", "sample_bist_1min")

print(df.head())