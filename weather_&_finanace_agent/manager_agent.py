from swarm import Swarm, Agent
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
import yfinance as yf
import os
import requests


load_dotenv()

# Initialize the swarm
client = Swarm()

# Initialize the FastAPI app
app = FastAPI()

# Step-1 Load OPENWEATHER API KEY For envronmental variables
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
if not OPENWEATHER_API_KEY:
    raise ValueError("OPENWEATHER_API_KEY environment variable is not set.")

# Step-2 Load OPENWEATHER BASE URL For envronmental variables
OPENWEATHER_BASE_URL = os.getenv("OPENWEATHER_BASE_URL")
if not OPENWEATHER_BASE_URL:
    raise ValueError("OPENWEATHER_BASE_URL environment variable is not set.")


# Function to get the weather data
def get_weather_data(city):
    url = f"{OPENWEATHER_BASE_URL}?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]
        city_name = data["name"]
        return f"The weather in {city_name} is {temperature}C with weather {weather_description}"

    else:
        return f"Could not get the weather for {city}.Please try again"


# Function Get Stock Price
def get_stock_price(ticker):
    print(f"Running stock price function for {ticker}...")
    stock = yf.Ticker(ticker)
    stock_info = stock.history(period="1d")
    if not stock_info.empty:
        latest_price = stock_info["Close"].iloc[-1]
        return f"The latest stock price for {ticker} is {latest_price}"
    else:
        return f"Could not get the stock price for {ticker}.Please try again"


# Function to transfer from manager agent to weather agent
def transfer_to_weather_agent():
    print(f"Transfering to weather agent...")
    return weather_agent


# Function to transfer from manager agent to finance agent
def transfer_to_finance_agent():
    print(f"Transfering to finance agent...")
    return finance_agent


# Manager Agent Call Weather / Finance Agent
manager_agent = Agent(
    name="Manager Assistant",
    instructions="You help users by directing them to the right assistant",
    functions=[transfer_to_weather_agent,transfer_to_finance_agent],
)

# Weather Agent Call Get Weather Function
weather_agent = Agent(
    name="Weather Assistant",
    instructions="You provide weather information for a given city using the provided tool.",
    functions=[get_weather_data],
)

# Finance Agent Call Get Stock Price Function
finance_agent = Agent(
    name="Finance Assistant",
    instructions="You provide the latest stock price for a given ticker.",
    functions=[get_stock_price],
)


@app.post("/manager-agent")
def get_message(message: str):
    try:
        response = client.run(
            agent=manager_agent,
            messages=[{"role": "user", "content": message}],
            

        )
        return {"message": response.messages[-1]["content"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Run the FastAPI app
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
