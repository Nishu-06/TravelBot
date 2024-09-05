from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)  # Flask app initialization

# Load and preprocess data
def load_and_preprocess_data():
    # Ensure your CSV path is correct
    file_path = 'hyderabad.csv'  # Replace with correct CSV path
    df = pd.read_csv(file_path)

    # Clean and preprocess data
    df['Price'] = df['Price'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Tax'] = df['Tax'].replace(r'[\$,]', '', regex=True).fillna(0).astype(float)
    df['Star Rating'] = df['Star Rating'].fillna(df['Star Rating'].median())
    df['Price After Tax'] = df['Price'] + df['Tax']

    # Drop unnecessary columns
    df.drop(['Nearest Landmark', 'Distance to Landmark'], axis=1, inplace=True)

    # Normalize Rating
    scaler = MinMaxScaler()
    df[['Rating']] = scaler.fit_transform(df[['Rating']])

    return df

# Recommendation route
@app.route('/recommendation', methods=['POST'])
def recommendation():
    req_data = request.get_json()
    user_inputs = req_data['queryResult']['parameters']

    # Load and preprocess the data
    df = load_and_preprocess_data()

    # Fetch user input preferences
    min_rating = float(user_inputs.get('min_rating', 0))
    max_price = float(user_inputs.get('max_price', float('inf')))
    
    # Normalize user-provided rating
    min_rating_normalized = min_rating / 5

    # Filter hotels based on user criteria
    filtered_hotels = df[(df['Rating'] >= min_rating_normalized) & (df['Price After Tax'] <= max_price)]

    # Sort hotels based on user preference
    sort_choice = user_inputs.get('sort_choice', 'rating').strip().lower()

    if sort_choice == 'rating':
        recommended_hotels = filtered_hotels.sort_values(by='Rating', ascending=False)
    elif sort_choice == 'price':
        recommended_hotels = filtered_hotels.sort_values(by='Price After Tax', ascending=True)
    elif sort_choice == 'both':
        recommended_hotels = filtered_hotels.sort_values(by=['Rating', 'Price After Tax'], ascending=[False, True])
    else:
        recommended_hotels = filtered_hotels.sort_values(by='Rating', ascending=False)
    
    # Prepare response based on recommendations
    if recommended_hotels.empty:
        response_text = "No hotels match your criteria. Please adjust your preferences."
    else:
        hotel_names = ', '.join(recommended_hotels['Hotel Name'].tolist())
        response_text = f"Recommended Hotels based on your preferences: {hotel_names}"
    
    # Return the response as JSON
    return jsonify({"fulfillmentText": response_text})

