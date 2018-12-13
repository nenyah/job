#%%
import pymongo

host = "localhost"
port = 27017
# 创建MONGODB数据库链接
client = pymongo.MongoClient(host=host, port=port)
# 指定数据库
job = client["job"]
cnnb = job["cnnb"]

#%%
list(cnnb.find())

#%%
import pandas as pd

#%%
df = pd.DataFrame(list(cnnb.find()))

#%%
df.info()

#%%
df.describe()

#%%
df.head()

#%%
