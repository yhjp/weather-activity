import streamlit as st
import requests
import datetime

# ✅ Open-Meteo의 Geocoding API 사용
def get_coordinates(city_name):
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "ko", "format": "json"}
    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        if "results" not in data or not data["results"]:
            return None, None
        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]
        return lat, lon
    except Exception as e:
        print("Error:", e)
        return None, None

# ✅ 날씨 + 대기질 불러오기
def get_weather_air(lat, lon):
    try:
        weather_url = "https://api.open-meteo.com/v1/forecast"
        air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

        params_weather = {
            "latitude": lat,
            "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "wind_speed_10m"]
        }
        params_air = {
            "latitude": lat,
            "longitude": lon,
            "current": ["pm2_5", "pm10", "us_aqi"]
        }

        weather_data = requests.get(weather_url, params=params_weather, timeout=10).json()
        air_data = requests.get(air_url, params=params_air, timeout=10).json()

        temp = weather_data.get("current", {}).get("temperature_2m")
        humidity = weather_data.get("current", {}).get("relative_humidity_2m")
        wind = weather_data.get("current", {}).get("wind_speed_10m")
        aqi = air_data.get("current", {}).get("us_aqi")
        return temp, humidity, wind, aqi
    except Exception as e:
        print("Error:", e)
        return None, None, None, None

# ✅ 활동 추천 로직
def recommend_activity(temp, humidity, wind, aqi):
    if aqi is None or temp is None:
        return "데이터를 불러올 수 없습니다."
    if aqi > 100:
        return "❌ 공기질이 나빠요! 실내활동을 추천합니다."
    elif temp > 32:
        return "🥵 너무 더워요! 이른 아침에만 가벼운 산책을 추천합니다."
    elif temp < 5:
        return "🥶 너무 추워요! 따뜻하게 입고 짧은 산책만 하세요."
    elif humidity > 80:
        return "💦 습도가 높아요. 실내 운동이 좋아요."
    elif wind > 8:
        return "🌬️ 바람이 강하네요. 자전거보단 산책이 좋아요."
    else:
        return "✅ 야외활동하기 좋은 날이에요! 조깅, 산책, 자전거 추천 🚴"

# ✅ Streamlit UI
st.set_page_config(page_title="야외활동 추천", page_icon="🌤️")
st.title("🌍 공기질 & 날씨 기반 야외활동 추천 앱")

city = st.text_input("도시 이름을 입력하세요 (한글/영문 모두 가능):", "서울")

if st.button("확인"):
    lat, lon = get_coordinates(city)
    if not lat:
        st.error("❗ 도시를 찾을 수 없습니다. 다시 입력해주세요.")
    else:
        temp, humidity, wind, aqi = get_weather_air(lat, lon)
        if temp is None:
            st.error("데이터를 불러올 수 없습니다.")
        else:
            st.success(f"📍 {city}의 현재 상황")
            st.write(f"🌡️ 온도: {temp}°C")
            st.write(f"💧 습도: {humidity}%")
            st.write(f"🌬️ 풍속: {wind} m/s")
            st.write(f"🌫️ 공기질 (AQI): {aqi}")
            st.markdown("### 🏖️ 추천 활동")
            st.info(recommend_activity(temp, humidity, wind, aqi))
            st.caption(f"업데이트: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}")
