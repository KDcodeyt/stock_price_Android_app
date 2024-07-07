from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime
from yahoo_getter import get_yahoo_finance_data
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def test():
    return jsonify({'message': 'Hello World'})

@app.route('/predict', methods=['POST', 'GET'])
def predict():
    # For demonstration, using hardcoded values
    stock = request.args.get('stock')
    num_days = request.args.get('num_days')
    print(stock, num_days)
    # stock = "GOOG"
    # num_days = 5
    end = datetime.now()
    start = datetime(end.year-20, end.month, end.day)
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")

    google_data = get_yahoo_finance_data(stock, start, end)
    
    model = load_model("Latest_stock_price_model.keras")

    splitting_len = int(len(google_data) * 0.7)
    x_test = pd.DataFrame(google_data['Close'][splitting_len:])

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(x_test[['Close']])

    x_data = []
    y_data = []

    for i in range(100, len(scaled_data)):
        x_data.append(scaled_data[i-100:i])
        y_data.append(scaled_data[i])

    x_data, y_data = np.array(x_data), np.array(y_data)

    predictions = model.predict(x_data)

    inv_pre = scaler.inverse_transform(predictions)
    inv_y_test = scaler.inverse_transform(y_data)

    plotting_data = {
        'original_test_data': inv_y_test.reshape(-1).tolist(),
        'predictions': inv_pre.reshape(-1).tolist()
    }

    last_100 = google_data[['Close']].tail(100)
    last_100_scaled = scaler.fit_transform(last_100['Close'].values.reshape(-1, 1)).reshape(1, -1, 1)

    def predict_future(no_of_days, prev_100):
        future_predictions = []
        for i in range(int(no_of_days)):
            next_day = model.predict(prev_100)
            prev_100 = np.append(prev_100[:, 1:, :], [[next_day[0]]], axis=1)
            future_predictions.append(float(scaler.inverse_transform(next_day)[0][0]))  # Convert to native float
        return future_predictions

    future_results = predict_future(num_days, last_100_scaled)
    temp = {"future_predictions":{}}
    for i in range(1,len(future_results)+1):
        temp["future_predictions"][f'day_{i}'] = str(future_results[i-1])
    # temp['future_predictions'] = future_results

    return jsonify(temp)

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0")
