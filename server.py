from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import requests

app = Flask(__name__)
CORS(app)

# 🔑 OpenAI
client = OpenAI(api_key="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")

# --------------------- CHATBOT ----------------------
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        user_message = data.get("message", "")
        if not user_message:
            return jsonify({"reply": "⚠️ Please type a message."})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )

        return jsonify({"reply": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"reply": f"❌ Error: {str(e)}"})


# --------------------- CROP GUIDE ----------------------
@app.route("/get_crop_guide", methods=["GET"])
def get_crop_guide():
    crop_name = request.args.get("crop", "").strip()
    if not crop_name:
        return jsonify({"error": "Please provide a crop name"}), 400
    try:
        prompt = f"Provide a detailed, step-by-step cultivation guide for {crop_name}."

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        return jsonify({"crop": crop_name, "guide": response.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------- WEATHER BY CITY ----------------------
@app.route("/weather", methods=["GET"])
def weather():
    try:
        city = request.args.get("city")
        if not city:
            return jsonify({"error": "Please provide a city parameter."})

        api_key = "7c3016110d97160987c597e8160fd8a6"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={api_key}"

        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return jsonify({"error": data.get("message", "City not found.")})

        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        condition = data["weather"][0]["description"]

        # -------- SAME CROP RECOMMENDATION AS get_weather ----------
        def get_crop_recommendation(temp, humidity, condition):
            condition = condition.lower()

            if temp < 20:
                return ["Wheat", "Barley", "Peas", "Cabbage", "Spinach"]

            if 20 <= temp <= 30:
                if "rain" in condition or humidity > 70:
                    return ["Rice", "Sugarcane", "Banana", "Turmeric"]
                else:
                    return ["Maize", "Ragi", "Groundnut", "Cotton", "Vegetables"]

            if temp > 30:
                if humidity > 60:
                    return ["Rice", "Sugarcane", "Millets", "Banana"]
                else:
                    return ["Bajra", "Jowar", "Cotton", "Groundnut"]

            return ["General crops: Vegetables, Pulses, Millets"]

        recommended_crops = get_crop_recommendation(temp, humidity, condition)

        return jsonify({
            "city": data["name"],
            "temperature": temp,
            "humidity": humidity,
            "condition": condition,
            "recommended_crops": recommended_crops   # <-- ADDED
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    # --------------------- LIVE WEATHER (LAT + LON) ----------------------
@app.route("/get_weather", methods=["POST"])
def get_weather():
    try:
        data = request.get_json()
        lat = data.get("lat")
        lon = data.get("lon")

        if lat is None or lon is None:
            return jsonify({"error": "Latitude or Longitude missing"}), 400

        api_key = "7c3016110d97160987c597e8160fd8a6"

        # -------- Reverse Geocoding ----------
        geo_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
        geo_data = requests.get(geo_url).json()
        city_name = geo_data[0]["name"] if geo_data else "Unknown Location"

        # -------- Weather API ----------
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={api_key}"
        weather_data = requests.get(url).json()

        if weather_data.get("cod") != 200:
            return jsonify({"error": weather_data.get("message", "Weather not found.")})

        temperature = weather_data["main"]["temp"]
        humidity = weather_data["main"]["humidity"]
        condition = weather_data["weather"][0]["description"]

        # -------- CROP RECOMMENDATION ----------
        def get_crop_recommendation(temp, humidity, condition):
            condition = condition.lower()

            if temp < 20:
                return ["Wheat", "Barley", "Peas", "Cabbage", "Spinach"]

            if 20 <= temp <= 30:
                if "rain" in condition or humidity > 70:
                    return ["Rice", "Sugarcane", "Banana", "Turmeric"]
                else:
                    return ["Maize", "Ragi", "Groundnut", "Cotton", "Vegetables"]

            if temp > 30:
                if humidity > 60:
                    return ["Rice", "Sugarcane", "Millets", "Banana"]
                else:
                    return ["Bajra", "Jowar", "Cotton", "Groundnut"]

            return ["General crops: Vegetables, Pulses, Millets"]

        crops = get_crop_recommendation(temperature, humidity, condition)

        return jsonify({
            "city": city_name,
            "temperature": temperature,
            "humidity": humidity,
            "condition": condition,
            "recommended_crops": crops
        })

    except Exception as e:
        return jsonify({"error": str(e)})



# --------------------- VEG PRICE ----------------------
@app.route("/veg_price", methods=["GET"])
def veg_price():
    try:
        veg = request.args.get("veg")
        market = request.args.get("market", "Local Market")

        if not veg:
            return jsonify({"error": "Please provide a vegetable or fruit name."})

        return jsonify({
            "vegetable": veg.capitalize(),
            "market": market,
            "modal_price": 20
        })

    except Exception as e:
        return jsonify({"error": str(e)})
    


    # --------------------- CROP GUIDE WITH TRANSLATION ----------------------

@app.route("/")
def home():
    return "✅ Flask server is running! Use /chat, /get_crop_guide, /weather, /veg_price."


if __name__ == "__main__":
    app.run(debug=True)
