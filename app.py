import streamlit as st
import requests

# -------------------------------
# 1️⃣ 도시명 → 좌표 변환
# -------------------------------
def get_coordinates(city_name):
    # 기본적인 한영 매핑
    city_map = {
        "서울": "Seoul",
        "부산": "Busan",
        "대구": "Daegu",
        "인천": "Incheon",
        "광주": "Gwangju",
        "대전": "Daejeon",
        "울산": "Ulsan",
        "제주": "Jeju",
        "하노이": "Hanoi",
        "도쿄": "Tokyo",
        "파리": "Paris",
        "뉴욕": "New York",
        "런던": "London",
        "베이징": "Beijing",
        "상하이": "Shanghai",
        "로스앤젤레스": "Los Angeles",
    }

    # 한글일 경우 영어로 변환
    if city_name in city_map:
        city_query = city_map[city_name]
    else:
        city_query = city_name

    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_query, "count": 1, "language": "en", "format": "json"}

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        # 결과 없으면 영어 이름으로 재시도
        if "results" not in data or not data["results"]:
            if city_query != city_name:
                params["name"] = city_name
                res = requests.get(url, params=params, timeout=10)
                data = res.json()

        if "results" not in data or not data["results"]:
            return None, None

        lat = data["results"][0]["latitude"]
        lon = data["results"][0]["longitude"]
        return lat, lon

    except Exception as e:
        st.error(f"위치 정보를 가져오는 중 오류 발생: {e}")
        return None, None


# -------------------------------
# 2️⃣ 날씨 및 공기질 데이터 가져오기
# -------------------------------
def get_weather(lat, lon):
    try:
        url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={lat}&longitude={lon}&current=pm10,pm2_5"
        )
        air = requests.get(url, timeout=10).json().get("current", {})

        url2 = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation"
            f"&timezone=auto"
        )
        weather = requests.get(url2, timeout=10).json().get("current", {})

        return {**weather, **air}
    except Exception as e:
        st.error(f"날씨 정보를 불러오는 중 오류 발생: {e}")
        return None


# -------------------------------
# 3️⃣ 야외활동 추천 로직
# -------------------------------
def recommend_activity(weather):
    if not weather:
        return "데이터를 불러올 수 없습니다."

    temp = weather.get("temperature_2m")
    humidity = weather.get("relative_humidity_2m")
    precipitation = weather.get("precipitation")
    pm10 = weather.get("pm10", 20)
    pm25 = weather.get("pm2_5", 10)

    if precipitation and precipitation > 0:
        return "비가 오니 실내 활동을 추천해요 ☔️"
    elif temp is not None and (temp < 0 or temp > 32):
        return "기온이 극단적이에요 🥵❄️ 실내에서 지내는 게 좋아요."
    elif pm10 > 80 or pm25 > 35:
        return "미세먼지가 많아요 😷 마스크 착용 또는 실내 활동 권장!"
    elif humidity and humidity > 85:
        return "습도가 높아요 💧 야외활동은 조금 불쾌할 수 있어요."
    else:
        return "야외활동하기 딱 좋은 날씨예요 ☀️ 산책이나 운동 어때요?"


# -------------------------------
# 4️⃣ Streamlit UI
# -------------------------------
st.set_page_config(page_title="야외활동 추천 웹앱 🌤️", layout="centered")

st.title("🌤️ 공기질·날씨 기반 야외활동 추천 웹앱")
st.write("영문 도시 이름을 입력하면 날씨와 활동 추천을 보여드려요!")

city = st.text_input("도시 이름을 입력하세요 (예: 서울, Tokyo, Paris, New York):")

if city:
    lat, lon = get_coordinates(city)

    if lat and lon:
        st.success(f"📍 {city}의 위치: ({lat:.2f}, {lon:.2f})")

        weather = get_weather(lat, lon)
        if weather:
            st.subheader("🌡️ 현재 날씨 정보")
            st.write(f"온도: {weather.get('temperature_2m', 'N/A')} °C")
            st.write(f"체감 온도: {weather.get('apparent_temperature', 'N/A')} °C")
            st.write(f"습도: {weather.get('relative_humidity_2m', 'N/A')}%")
            st.write(f"강수량: {weather.get('precipitation', 'N/A')} mm")
            st.write(f"미세먼지(PM10): {weather.get('pm10', 'N/A')} µg/m³")
            st.write(f"초미세먼지(PM2.5): {weather.get('pm2_5', 'N/A')} µg/m³")

            st.subheader("🎯 활동 추천")
            st.info(recommend_activity(weather))
        else:
            st.error("날씨 데이터를 가져오지 못했습니다.")
    else:
        st.error("도시를 찾을 수 없습니다. 다른 이름으로 시도해보세요.")
