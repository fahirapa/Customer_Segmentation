# -*- coding: utf-8 -*-
"""Fahira_Customer_Segmentation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1A7I6WL515EOvwRl5jURlE7CY4tYSV76v
"""

!pip install squarify



"""## Inisialisasi Library"""

#Import Library
import pandas as pd # import pandas module to read the data
import io # import io module to read the data
import numpy as np # import numpy module for numeric computation
import matplotlib.pyplot as plt #import matplotlib.pyplot for graphical plotting
import seaborn as sns #import seaborn of matplotlib for statistical graphic 
import squarify # import squarify for creating treemaps
import datetime as dt #import datetime dor manipulating date and time

# read file
from google.colab import files # import files module to upload data file
uploaded = files.upload() # upload file

df = pd.read_csv(io.BytesIO(uploaded['Customer_Segmentation_Data.csv'])) # read  the dataset
df.head()

# DATA EXPLORATION

df['Customer ID'] = df['Customer ID'].astype(str) # change Customer ID data type from float64 into string
df.info()

df.describe().T # statistics descriptive for numeric atribut

df['Description'].nunique() #number of unique products

df1 = df[df["Quantity"] > 0] #drop the negative value of the Quantity
a=df1.groupby('Description').agg({'Quantity':'sum'}) # the most ordered products
a.sort_values(by='Quantity',ascending=False) # sort the products by the most ordered

df1 = df1[df1["Price"] > 0] #drop the negative value of the Price Atribut
df1["TotalPrice"] = df1["Quantity"] * df1["Price"] # create total price atribut
df1.groupby('Country').agg({'TotalPrice':'sum'}).sort_values('TotalPrice',ascending=False).head() #total earn from each country sort by the highest

### DATA PREPARATION ###

# check percentage of null values
((df1.isnull().sum())/(df.shape[0])*100).sort_values(ascending=False)

df.shape #data shape

df1.describe().T # statistic descriptive

### RFM ###

df1

# RECENCY

df1['InvoiceDate'] = pd.to_datetime(df1['InvoiceDate']) # convert string Date time into Python Date time object
max_date = max(df1['InvoiceDate']) # last transaction
df1['Recency'] = max_date - df1['InvoiceDate'] # Calculate difference between the last transaction and the invoice date

# create dataset for atribut Recency
rfm_p = df1.groupby('Customer ID')['Recency'].min()
rfm_p = rfm_p.reset_index()

# Extract number of days
rfm_p['Recency'] = rfm_p['Recency'].dt.days
rfm_p.head()

# Frequency 
rfm_f = df1.groupby('Customer ID')['Invoice'].count() # count the total purchase of each customer, group by dustomer ID
rfm_f = rfm_f.reset_index() # reset index
rfm_f.columns = ['Customer ID', 'Frequency'] # name the column
rfm_f.head()

# Monetary
rfm_m = df1.groupby('Customer ID')['TotalPrice'].sum() # total price per Customer ID
rfm_m = rfm_m.reset_index() # reset index
rfm_m.columns = ['Customer ID', 'Monetary'] # name the column
rfm_m.head()

# Merge dataframe 
rfm = pd.merge(rfm_m, rfm_f, on='Customer ID', how='inner')
rfm = pd.merge(rfm, rfm_p, on='Customer ID', how='inner')
rfm.columns = ['CustomerID', 'Monetary', 'Frequency', 'Recency']
rfm.head()



## RFM SCORE

# Calculating RFM Score based on quantile
# Recency, 3 = Most recent, 1 = least . 
rfm["recency_score"] = pd.qcut(rfm['Recency'], 3, labels=[ 3, 2, 1])

#Frequency, 3 = Most frequent, 1 = rarely
rfm["frequency_score"] = pd.qcut(rfm['Frequency'].rank(method="first"), 3, labels=[1, 2, 3])

#Monetary, 3 = best, 1 = least
rfm["monetary_score"] = pd.qcut(rfm['Monetary'], 3, labels=[1, 2, 3])
rfm.head(5)

# Concating the RFM quartile values to create RFM Segments
rfm["RFM_Segment"] = (rfm['recency_score'].astype(str) +
                    rfm['frequency_score'].astype(str) + rfm['monetary_score'].astype(str))
rfm

# Count num of unique segments
rfm_count_unique = rfm.groupby('RFM_Segment')['RFM_Segment'].nunique()
print(rfm_count_unique.sum())
# Calculate RFM_Score
rfm['RFM_Score'] = rfm[['recency_score','frequency_score','monetary_score']].sum(axis=1)
print(rfm['RFM_Score'].head())

# Define rfm_segment function
def rfm_segment(df1):
    if df1['RFM_Score'] >= 9:
        return 'Best Customers'
    elif ((df1['RFM_Score'] >= 8) and (df1['RFM_Score'] < 9)):
        return 'Loyal/Commited'
    elif ((df1['RFM_Score'] >= 7) and (df1['RFM_Score'] < 8)):
        return 'Potential'
    elif ((df1['RFM_Score'] >= 6) and (df1['RFM_Score'] < 7)):
        return 'Promising'
    elif ((df1['RFM_Score'] >= 5) and (df1['RFM_Score'] < 6)):
        return 'Requires Attention'
    else:
        return 'Demands Activation'
# Create a new variable RFM_segment
rfm['RFM_segment'] = rfm.apply(rfm_segment, axis=1)
# Printing the header with top 15 rows 
rfm.head(15)

# Calculate average values for each RFM_segment, and return a size of each segment 
rfm_segment_agg = rfm.groupby('RFM_segment').agg({
    'Recency': 'mean',
    'Frequency': 'mean',
    'Monetary': ['mean', 'count']
}).round(1)
# Print the aggregated dataset
print(rfm_segment_agg)

# check that the customers have been assigned to the correct segment by counting the number with each segment
rfm.groupby('RFM_segment').agg(
    customers=('CustomerID', 'count'),
    min_rfm=('RFM_Segment', 'min'),
    max_rfm=('RFM_Segment', 'max'),
).reset_index().sort_values(by='min_rfm')

# Check the minimum and maximum value of Recency, Frequency, Monetary in each segments 
rfm.groupby('RFM_segment').agg(
    min_recency=('Recency', 'min'),
    max_recency=('Recency', 'max'),
    min_frequency=('Frequency', 'min'),
    max_frequency=('Frequency', 'max'),
    min_monetary=('Monetary', 'min'),
    max_monetary=('Monetary', 'max'),
).reset_index().sort_values(by='min_recency')

# SQUARIFY PLOT
rfm_segment_agg.columns = ['RecencyMean','FrequencyMean','MonetaryMean', 'Count'] # create atribut name for the table
#Create our plot and resize it.
fig = plt.gcf() # get the current figure
ax = fig.add_subplot() # add subplot
fig.set_size_inches(16,9) #figure size
colors = ["orange", "blue", "purple", "brown", "red", "green"] # color per segments
squarify.plot(sizes=rfm_segment_agg['Count'], 
              label=['Best Customers',
                     'Demands Activation',
                     'Loyal/Commited',
                     'Potential', 
                     'Promising',
                     'Requires Attention'
                     ], alpha=.6, color = colors) #squarify plot
plt.title("RFM Segments",fontsize=18,fontweight="bold") #plot title
plt.axis('off') #do not show axis
plt.show() #show plot

# create a table of the number of customer each segment
sq1 = rfm.groupby('RFM_segment')['CustomerID'].nunique().sort_values(ascending=False).reset_index() 
# create the bar plot 
plt.figure(figsize=(14,7))
sns.barplot(data=sq1, x='RFM_segment', y='CustomerID')

plt.pie(rfm.RFM_segment.value_counts(),
        labels=rfm.RFM_segment.value_counts().index,
        autopct='%.0f%%') # Create Pie Plot of the percentage of customer distribution
plt.show()

