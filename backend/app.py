from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

# Load and prepare data
df = pd.read_csv('weather_data.csv')

# Convert Date_Time to datetime format
df['Date_Time'] = pd.to_datetime(df['Date_Time'])
df.sort_values(by=['Location', 'Date_Time'], inplace=True)

# Extract 'hour' from Date_Time to help with daily cycles
df['hour'] = df['Date_Time'].dt.hour

# Train models for each location
location_models = {}

for location in df['Location'].unique():
    loc_df = df[df['Location'] == location].copy()
    loc_df['Timestamp'] = loc_df['Date_Time'].astype('int64') // 10**9  # Unix timestamp

    X = loc_df[['Timestamp', 'hour']]  # Include hour as a feature
    y_temp = loc_df['Temperature_C']
    y_humidity = loc_df['Humidity_pct']
    y_wind_speed = loc_df['Wind_Speed_kmh']
    y_precipitation = loc_df['Precipitation_mm']

    temp_model = LinearRegression().fit(X, y_temp)
    humidity_model = LinearRegression().fit(X, y_humidity)
    wind_speed_model = LinearRegression().fit(X, y_wind_speed)
    precipitation_model = LinearRegression().fit(X, y_precipitation)

    location_models[location] = {
        'temp_model': temp_model,
        'humidity_model': humidity_model,
        'wind_speed_model': wind_speed_model,
        'precipitation_model': precipitation_model
    }

@app.route('/locations')
def get_locations():
    return jsonify(sorted(df['Location'].unique().tolist()))

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    location = data.get('location')

    if not location or location not in location_models:
        return jsonify({'error': 'Invalid or missing location'}), 400

    models = location_models[location]
    base_time = datetime.now()  # Use current system time as the base

    predictions = []

    for i in range(1, 25):  # Next 24 hours
        future_time = base_time + timedelta(hours=i)
        future_timestamp = int(future_time.timestamp())

        # Use both timestamp and hour of day for prediction
        hour_of_day = future_time.hour

        # Predict for temperature, humidity, wind speed, and precipitation
        temp = models['temp_model'].predict([[future_timestamp, hour_of_day]])[0]
        humidity = models['humidity_model'].predict([[future_timestamp, hour_of_day]])[0]
        wind_speed = models['wind_speed_model'].predict([[future_timestamp, hour_of_day]])[0]
        precipitation = models['precipitation_model'].predict([[future_timestamp, hour_of_day]])[0]

        predictions.append({
            'hour': future_time.strftime("%Y-%m-%d %H:%M"),
            'temperature': round(temp, 2),
            'humidity': round(humidity, 2),
            'wind_speed': round(wind_speed, 2),
            'precipitation': round(precipitation, 2)
        })

    return jsonify(predictions)

if __name__ == '__main__':
    app.run(debug=True)
