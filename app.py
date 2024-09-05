from flask import Flask, request, jsonify
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

app = Flask(__name__)  # Corrected line

# Load and preprocess data
def load_and_preprocess_data():
    file_path = r'C:\Users\asus\Desktop\hyderabad.csv'  # Use raw string literal
    df = pd.read_csv(file_path)
    df['Price'] = df['Price'].replace(r'[\$,]', '', regex=True).astype(float)
    df['Tax'] = df['Tax'].replace(r'[\$,]', '', regex=True).fillna(0).astype(float)
    df['Star Rating'] = df['Star Rating'].fillna(df['Star Rating'].median())
    df['Price After Tax'] = df['Price'] + df['Tax']
    df.drop(['Nearest Landmark', 'Distance to Landmark'], axis=1, inplace=True)
    scaler = MinMaxScaler()
    df[['Rating']] = scaler.fit_transform(df[['Rating']])
    return df

@app.route('/recommendation', methods=['POST'])
def recommendation():
    req_data = request.get_json()
    user_inputs = req_data['queryResult']['parameters']
    
    # Load and preprocess data
    df = load_and_preprocess_data()

    min_rating = float(user_inputs.get('min_rating', 0))
    max_price = float(user_inputs.get('max_price', float('inf')))
    
    min_rating_normalized = min_rating / 5

    filtered_hotels = df[(df['Rating'] >= min_rating_normalized) & (df['Price After Tax'] <= max_price)]
    
    sort_choice = user_inputs.get('sort_choice', 'rating').strip().lower()

    if sort_choice == 'rating':
        recommended_hotels = filtered_hotels.sort_values(by='Rating', ascending=False)
    elif sort_choice == 'price':
        recommended_hotels = filtered_hotels.sort_values(by='Price After Tax', ascending=True)
    elif sort_choice == 'both':
        recommended_hotels = filtered_hotels.sort_values(by=['Rating', 'Price After Tax'], ascending=[False, True])
    else:
        recommended_hotels = filtered_hotels.sort_values(by='Rating', ascending=False)
    
    if recommended_hotels.empty:
        response_text = "No hotels match your criteria. Please adjust your preferences."
    else:
        hotel_names = ', '.join(recommended_hotels['Hotel Name'].tolist())
        response_text = f"Recommended Hotels based on your preferences: {hotel_names}"
    
    return jsonify({"fulfillmentText": response_text})

if __name__ == "__main__":
    app.run(debug=True)
