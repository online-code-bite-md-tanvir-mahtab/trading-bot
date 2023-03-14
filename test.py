import pandas as pd
import plotly.express as px
import streamlit as st
import requests
from datetime import datetime

# now i am going to create a method that will add some column
# and this method will normalize the data
def data_processing(stock_data):
  new_dates = []
  for tim in stock_data['Date']:
    date = tim
    import datetime
    # Convert milliseconds to seconds
    seconds = date / 1000

    # Create a datetime object from the Unix timestamp
    dt = datetime.datetime.fromtimestamp(seconds)
    new_dates.append(str(dt.date()))
  # now i am going to convert the current date column with the new on
  stock_data['Date'] = new_dates
  stock_data.head()
  # create the price change value
  # for creating the price_change column
  change = stock_data['Close'].diff()
  # creating the gain and loss column
  gain = change.where(change>0,0)
  loss = -change.where(change<0,0)
  # creating the avg of the gain and loss
  avg_gain = gain.rolling(14).mean()
  avg_loss = loss.rolling(14).mean()
  # calculating the rs value
  rs = avg_gain/avg_loss
  # calculating the rsi value
  rsi = 100 - (100 / (1 + rs))
  stock_data['RSI'] = rsi
  stock_data['Price_Change'] = change
  stock_data['RSI'].fillna(stock_data['RSI'].mean(),inplace=True)
  stock_data['Price_Change'].fillna(stock_data['Price_Change'].mean(),inplace=True)
  # normalizing the data
  features = stock_data[['Open','High','Low','Close','RSI','Price_Change']].values
  return features,stock_data



def predict_the_data(test_data):
  from tensorflow.keras.models import load_model
  model = load_model('./trading_bot.h5')
  y_pred = model.predict(test_data)
  lss,acc = model.evaluate(test_data,y_pred)
  # for result showcase
  if y_pred.all() > 0.5:
    pre = {
      'Gain':int(round(acc*100)),
      'Loss':int(100 - round(acc*100))
    }
    return pre
  else:
    pre = {
      'Gain':int(100 - round(acc*100)),
      'Loss':int(round(acc*100))
    }
    return pre


def predected_all_row_datas(test_data):
  new_test_data = []

  for i in range(len(test_data)):
    if i ==0:
      pass
    else:
      new_test_data.append(predict_the_data(test_data[:i]))
  sell = pd.DataFrame(new_test_data)
  for i in range(len(sell)):
    try:
      sell['Gain'][i] = sell['Gain'][i][0]
      sell['Loss'][i] = sell['Loss'][i][0]
    except Exception:
      sell['Gain'][i] = sell['Gain'][i]
      sell['Loss'][i] = sell['Loss'][i]
  return sell


def another_processing(s_data,buy_sell):
  buy_sell = buy_sell.set_index(s_data.index[:len(s_data)-1])
  s_data['Gain'] = buy_sell['Gain']
  s_data['Loss'] = buy_sell['Loss']
  return s_data

# bassic configuration
st.set_page_config(
    page_title='Trading Ea Dashboard or Cpanel',
    page_icon=":chart:",
    layout='wide'
)

t = str(datetime.datetime.now().date())
web_url = f'https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2000-01-09/{t}?adjusted=true&sort=asc&limit=10000&apiKey=dComuxapOAuv4bbJiCzANe9Eg_bEp1Wn'

response = requests.get(url=web_url)
data = response.json()
result = data['results']
# print(result)


Volume = []
Open = []
Close = []
High = []
Low = []
Date = []

for key,value in enumerate(result):
  Volume.append(value['v'])
  Open.append(value['o'])
  Close.append(value['c'])
  High.append(value['h'])
  Low.append(value['l'])
  Date.append(value['t'])
  
stock_data = pd.DataFrame({
    'Date':Date,
    'Open':Open,
    'High':High,
    'Low':Low,
    'Close':Close,
    'Volume':Volume
})




st.sidebar.title('start date')
start_date = st.sidebar.date_input('Enter you start date')

st.sidebar.title('end date')
end_date = st.sidebar.date_input('Enter you end date')

st.sidebar.title('Prediction Probability')
pat = st.sidebar.text_input('Enter you PAT%')

# if start_date == '' and end_date == '':
#   test_data,stock_data = data_processing(stock_data)
#   # to show the data in streamlit
#   st.dataframe(stock_data)
# else:
date_str = str(start_date)
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
milliseconds = int(date_obj.timestamp() * 1000)
start_date = milliseconds
date_str = str(end_date)
date_obj = datetime.strptime(date_str, "%Y-%m-%d")
milliseconds = int(date_obj.timestamp() * 1000)
end_date = milliseconds
filter_data = stock_data.loc[(stock_data['Date'] >= start_date) & (stock_data['Date'] <= end_date)]
test_data,stock_data = data_processing(filter_data)
st.dataframe(stock_data)



# creating the bar chart
high_and_date = px.bar(
    stock_data,
    x='High',
    y=stock_data['Date'],
    orientation='h',
    title='<b>High base on Date</b>',
    color=['#0083BB'] * len(stock_data),
    template='plotly_white',
)
# high_and_low.update_layout(
#     plot_bgcolor="#ffffff",
#     xaxis = (dict(showgrid=False))
# )


low_and_date = px.bar(
    stock_data,
    x='Date',
    y=stock_data['Low'],
    orientation='v',
    title='<b>Low base on Date</b>',
    color=['#0083BB'] * len(stock_data),
    template='plotly_white',
)

left_column,right_column = st.columns(2)

left_column.plotly_chart(high_and_date,use_container_width=True)
right_column.plotly_chart(low_and_date,use_container_width=True)


ea_close = px.line(
    stock_data,
    x='Date',
    y=stock_data['Close'],
    title='<b>EA Graph</b>',
    color=['#0083BB'] * len(stock_data),
    template='plotly_white',
    
)

# st.plotly_chart(ea_close)


ea_rsi = st.line_chart(
    stock_data[['Date','Open','Close','RSI']],
    x='Date'
)




import streamlit as st
import time
if stock_data.empty:
  pass
else:
  buy_sell = predected_all_row_datas(test_data)
  stock_data = another_processing(stock_data,buy_sell)
  # stock_data.loc[(stock_data['Gain']<=70) | (stock_data['Loss'] <= 70)]
  # t_data,s_data = data_processing(stock_data)
  ea_rsi = st.line_chart(
      stock_data[['Date','Open','Close','RSI','Gain','Loss']],
      x='Date'
  )
  st.text(body="Prediction")
  progress_text = "Buy"
  my_bar = st.progress(0, text=progress_text)
  dict_data = predict_the_data(test_data)
  for percent_complete in range(dict_data['Gain']):
      my_bar.progress(percent_complete + 1, text=progress_text)
  my_bar2 = st.progress(0,text='Sell')
  for percent_complete in range(dict_data['Loss']):
      my_bar2.progress(percent_complete + 1, text='Sell')