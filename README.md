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
### Response Format
Example response for wave information:

```json
{
    "bairro": "Copacabana",
    "altura_onda": 1.5,
    "direcao": "Sudeste",
    "periodo": 8.5,
    "temperatura_agua": 22.5,
    "vento_velocidade": 15.2,
    "vento_direcao": "Leste",
    "timestamp": "2023-11-15T14:30:00",
    "fonte": "OpenWeatherMap"
}
 ```
 ## Error Handling
The API includes fallback mechanisms:

1. Tries OpenWeatherMap API first
2. Falls back to Stormglass API if OpenWeatherMap fails
3. Uses simulated data if both APIs are unavailable
## Cache System
- Wave information is cached for 1 hour to reduce API calls
- Cache is stored in memory and resets when the server restarts
## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
## License
This project is licensed under the MIT License - see the LICENSE file for details
## Technologies
- FastAPI
- HTMX
- Tailwind CSS
- OpenWeatherMap API
- Stormglass API