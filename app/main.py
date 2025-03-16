from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variables
OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
STORMGLASS_API_KEY = os.getenv("STORMGLASS_API_KEY")  # Add this line

if not OPENWEATHERMAP_API_KEY:
    print("Warning: OpenWeatherMap API key not found in environment variables")
else:
    print("OpenWeatherMap API Key loaded successfully")

if not STORMGLASS_API_KEY:
    print("Warning: Stormglass API key not found in environment variables")
else:
    print("Stormglass API Key loaded successfully")

app = FastAPI(
    title="BoasOndas API",
    description="API para coleta de informações de ondas nos bairros do Rio de Janeiro",
    version="1.0.1"
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Modelo de dados para informações de ondas
class WaveInfo(BaseModel):
    bairro: str
    altura_onda: float
    direcao: str
    periodo: float
    temperatura_agua: float
    vento_velocidade: float
    vento_direcao: str
    timestamp: datetime
    fonte: str = "Simulado"  # Indica a fonte dos dados

# Banco de dados simulado (em memória)
wave_database = {}

# Coordenadas geográficas dos bairros do Rio de Janeiro com praias
bairros_coords = {
    "Copacabana": {"lat": -22.9714, "lon": -43.1823},
    "Ipanema": {"lat": -22.9837, "lon": -43.1985},
    "Leblon": {"lat": -22.9864, "lon": -43.2233},
    "Barra da Tijuca": {"lat": -23.0089, "lon": -43.3220},
    "Recreio dos Bandeirantes": {"lat": -23.0279, "lon": -43.4779},
    "São Conrado": {"lat": -22.9997, "lon": -43.2563},
    "Leme": {"lat": -22.9642, "lon": -43.1709},
    "Arpoador": {"lat": -22.9892, "lon": -43.1919},
    "Prainha": {"lat": -23.0404, "lon": -43.5019},
    "Grumari": {"lat": -23.0486, "lon": -43.5305},
    "Flamengo": {"lat": -22.9375, "lon": -43.1747},
    "Botafogo": {"lat": -22.9507, "lon": -43.1845},
    "Urca": {"lat": -22.9486, "lon": -43.1658},
    "Joatinga": {"lat": -23.0166, "lon": -43.2833},
    "Macumba": {"lat": -23.0333, "lon": -43.4833},
    "Pontal": {"lat": -23.0333, "lon": -43.4667},
    "Pepê": {"lat": -23.0089, "lon": -43.3220},
    "Diabo": {"lat": -22.9892, "lon": -43.1919},
    "Reserva": {"lat": -23.0279, "lon": -43.4779}
}

# Lista de bairros do Rio de Janeiro com praias
bairros_rj = list(bairros_coords.keys())

# Função para obter dados reais de previsão marítima
def get_openweather_free_data(bairro: str):
    if not OPENWEATHERMAP_API_KEY:
        return None
    
    coords = bairros_coords.get(bairro)
    if not coords:
        return None
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        
        wind_speed = weather_data.get("wind", {}).get("speed", 0) * 3.6
        wind_direction_deg = weather_data.get("wind", {}).get("deg", 0)
        
        wind_directions = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste", "Norte"]
        wind_direction = wind_directions[round(wind_direction_deg / 45) % 8]
        
        # Simular alguns dados que não estão disponíveis na API gratuita
        import random
        wave_height = round(random.uniform(0.5, 3.0) * (wind_speed / 20), 1)  # Simular altura baseada no vento
        wave_period = round(random.uniform(5.0, 15.0), 1)
        water_temp = round(weather_data.get("main", {}).get("temp", 20) - 2, 1)  # Temperatura da água geralmente menor que do ar
        
        # Determinar direção das ondas (geralmente relacionada à direção do vento)
        wave_directions = ["Leste", "Sudeste", "Sul", "Sudoeste"]
        wave_direction = random.choice(wave_directions)
        
        return {
            "altura_onda": wave_height,
            "direcao": wave_direction,
            "periodo": wave_period,
            "temperatura_agua": water_temp,
            "vento_velocidade": round(wind_speed, 1),
            "vento_direcao": wind_direction,
            "fonte": "OpenWeatherMap Free"
        }
    except Exception as e:
        print(f"Erro ao obter dados do OpenWeatherMap Free: {e}")
        return None

def get_openweather_onecall_data(bairro: str):
    if not OPENWEATHERMAP_API_KEY:
        return None
    
    coords = bairros_coords.get(bairro)
    if not coords:
        return None
    
    try:
        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={coords['lat']}&lon={coords['lon']}&exclude=minutely,hourly,daily,alerts&appid={OPENWEATHERMAP_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        weather_data = response.json()
        
        current = weather_data.get("current", {})
        wind_speed = current.get("wind_speed", 0) * 3.6
        wind_direction_deg = current.get("wind_deg", 0)
        
        wind_directions = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste", "Norte"]
        wind_direction = wind_directions[round(wind_direction_deg / 45) % 8]
        
        return {
            "altura_onda": round(current.get("wave_height", 0), 1),
            "direcao": wind_direction,
            "periodo": round(current.get("wave_period", 8.0), 1),
            "temperatura_agua": round(current.get("temp", 20), 1),
            "vento_velocidade": round(wind_speed, 1),
            "vento_direcao": wind_direction,
            "fonte": "OpenWeatherMap OneCall"
        }
    except Exception as e:
        print(f"Erro ao obter dados do OpenWeatherMap OneCall: {e}")
        return None

@app.get("/ondas/{bairro}")
def get_wave_info(bairro: str):
    if bairro not in bairros_rj:
        raise HTTPException(status_code=404, detail=f"Bairro {bairro} não encontrado ou não possui praia")
    
    current_time = datetime.now()
    if bairro in wave_database and (current_time - wave_database[bairro].timestamp).seconds < 3600:
        return wave_database[bairro]
    
    # Try OpenWeatherMap Free API first
    real_data = get_openweather_free_data(bairro)
    
    # If Free API fails, try OpenWeatherMap OneCall API
    if not real_data:
        real_data = get_openweather_onecall_data(bairro)
    
    # If OneCall fails, try Stormglass
    if not real_data:
        # Define Stormglass API function before using it
        def get_stormglass_data(bairro: str):
            if not STORMGLASS_API_KEY:
                return None
            
            coords = bairros_coords.get(bairro)
            if not coords:
                return None
            
            try:
                url = f"https://api.stormglass.io/v2/weather/point?lat={coords['lat']}&lng={coords['lon']}&params=waveHeight,waveDirection,wavePeriod,waterTemperature,windSpeed,windDirection"
                headers = {'Authorization': STORMGLASS_API_KEY}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                # Get first hour of forecast data
                current = data.get('hours', [{}])[0]
                
                # Convert wave direction to cardinal points
                wave_dir_deg = current.get('waveDirection', {}).get('noaa', 0)
                wind_dir_deg = current.get('windDirection', {}).get('noaa', 0)
                
                directions = ["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]
                wave_direction = directions[int((wave_dir_deg + 22.5) % 360) // 45]
                wind_direction = directions[int((wind_dir_deg + 22.5) % 360) // 45]
                
                return {
                    "altura_onda": round(current.get('waveHeight', {}).get('noaa', 0), 1),
                    "direcao": wave_direction,
                    "periodo": round(current.get('wavePeriod', {}).get('noaa', 8.0), 1),
                    "temperatura_agua": round(current.get('waterTemperature', {}).get('noaa', 20), 1),
                    "vento_velocidade": round(current.get('windSpeed', {}).get('noaa', 0) * 3.6, 1),
                    "vento_direcao": wind_direction,
                    "fonte": "Stormglass"
                }
            except Exception as e:
                print(f"Error getting data from Stormglass: {e}")
                return None
                
        real_data = get_stormglass_data(bairro)
    
    if real_data:
        wave_info = WaveInfo(
            bairro=bairro,
            altura_onda=real_data["altura_onda"],
            direcao=real_data["direcao"],
            periodo=real_data["periodo"],
            temperatura_agua=real_data["temperatura_agua"],
            vento_velocidade=real_data["vento_velocidade"],
            vento_direcao=real_data["vento_direcao"],
            timestamp=current_time,
            fonte=real_data["fonte"]
        )
    else:
        # Fallback to simulation if all APIs fail
        import random
        wave_info = WaveInfo(
            bairro=bairro,
            altura_onda=round(random.uniform(0.5, 3.0), 1),
            direcao=random.choice(["Leste", "Sudeste", "Sul", "Sudoeste"]),
            periodo=round(random.uniform(5.0, 15.0), 1),
            temperatura_agua=round(random.uniform(18.0, 26.0), 1),
            vento_velocidade=round(random.uniform(0, 30.0), 1),
            vento_direcao=random.choice(["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]),
            timestamp=current_time,
            fonte="Simulado"
        )
    
    wave_database[bairro] = wave_info
    return wave_info

@app.get("/ui/ondas/{bairro}", include_in_schema=False)
async def get_wave_info_ui(bairro: str, request: Request):
    """HTML endpoint for wave information"""
    wave_info = get_wave_info(bairro)
    return templates.TemplateResponse("wave_info.html", {"request": request, "wave_info": wave_info})

@app.get("/ondas", response_model=List[WaveInfo])
def get_all_wave_info():
    """Retorna informações de ondas para todos os bairros"""
    result = []
    current_time = datetime.now()
    
    for bairro in bairros_rj:
        if bairro in wave_database:
            result.append(wave_database[bairro])
        else:
            # Create wave info without using get_wave_info function
            real_data = get_openweather_free_data(bairro)
            if not real_data:
                real_data = get_openweather_onecall_data(bairro)
            if not real_data:
                # Fallback to simulation
                import random
                real_data = {
                    "altura_onda": round(random.uniform(0.5, 3.0), 1),
                    "direcao": random.choice(["Leste", "Sudeste", "Sul", "Sudoeste"]),
                    "periodo": round(random.uniform(5.0, 15.0), 1),
                    "temperatura_agua": round(random.uniform(18.0, 26.0), 1),
                    "vento_velocidade": round(random.uniform(0, 30.0), 1),
                    "vento_direcao": random.choice(["Norte", "Nordeste", "Leste", "Sudeste", "Sul", "Sudoeste", "Oeste", "Noroeste"]),
                    "fonte": "Simulado"
                }
            
            wave_info = WaveInfo(
                bairro=bairro,
                altura_onda=real_data["altura_onda"],
                direcao=real_data["direcao"],
                periodo=real_data["periodo"],
                temperatura_agua=real_data["temperatura_agua"],
                vento_velocidade=real_data["vento_velocidade"],
                vento_direcao=real_data["vento_direcao"],
                timestamp=current_time,
                fonte=real_data["fonte"]
            )
            wave_database[bairro] = wave_info
            result.append(wave_info)
    
    return result

# Add a new route for the frontend
@app.get("/ui", include_in_schema=False)
async def get_ui(request: Request):
    """Serve the frontend UI"""
    return templates.TemplateResponse("index.html", {
        "request": request,
        "bairros": bairros_rj
    })

@app.get("/bairros")
def get_bairros(request: Request):
    """Retorna a lista de bairros disponíveis para consulta"""
    return bairros_rj

@app.get("/")
def read_root(request: Request):
    """Root endpoint with API documentation"""
    accept = request.headers.get("accept", "")
    api_info = {
        "name": "BoasOndas API",
        "version": "1.0.1",
        "description": "API para informações de ondas nas praias do Rio de Janeiro",
        "endpoints": {
            "/": "Esta página - Informações básicas da API",
            "/ui": "Interface web para visualização dos dados",
            "/bairros": "Lista de praias/bairros disponíveis",
            "/ondas/{bairro}": "Informações detalhadas de ondas para um bairro específico",
            "/ondas": "Informações de ondas para todos os bairros"
        },
        "examples": {
            "Listar bairros": "/bairros",
            "Dados de Copacabana": "/ondas/Copacabana",
            "Interface Web": "/ui"
        }
    }
    
    if "text/html" in accept or "application/xhtml+xml" in accept:
        return templates.TemplateResponse("api_info.html", {"request": request, "api_info": api_info})
    return api_info

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7000, reload=True)