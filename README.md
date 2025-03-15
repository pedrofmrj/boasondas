# BoasOndas

Wave information API for Rio de Janeiro beaches. This application provides real-time wave and weather data for various beaches in Rio de Janeiro.

## Features

- Real-time wave height information
- Wind speed and direction
- Water temperature
- Wave period and direction
- Support for multiple beaches in Rio de Janeiro
- HTMX-powered frontend with Tailwind CSS

## Setup

1. Clone the repository
2. Install dependencies:

```python
pip install -r requirements.txt

Create a .env file with your API keys:
```plaintext
OPENWEATHERMAP_API_KEY=your_key_here
STORMGLASS_API_KEY=your_key_here
 ```

4. Run the application:
```python
python app/main.py
 ```

5. Access the application at http://localhost:7000/ui
## API Endpoints
- /ui - Frontend interface
- /bairros - List of available beaches
- /ondas/{bairro} - Wave information for a specific beach
- /ondas - Wave information for all beaches
## Technologies
- FastAPI
- HTMX
- Tailwind CSS
- OpenWeatherMap API
- Stormglass API