"""
Climate data fetcher for external APIs
"""
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json
from config import settings

logger = logging.getLogger(__name__)

class ClimateDataFetcher:
    """Fetches data from various climate and environmental APIs"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ClimateIQ-Platform/1.0'
        })
    
    def get_weather_data(self, location: str) -> Dict[str, Any]:
        """Fetch current weather data from OpenWeatherMap"""
        try:
            url = f"{settings.OPENWEATHER_API_BASE}/weather"
            params = {
                'q': location,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'location': data.get('name', location),
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'weather': data['weather'][0]['description'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")
            return {'error': str(e), 'location': location}
    
    def get_air_quality_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """Fetch air quality data from OpenWeatherMap"""
        try:
            url = f"{settings.OPENWEATHER_API_BASE.replace('/data/2.5', '')}/data/2.5/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': settings.OPENWEATHER_API_KEY
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'list' in data and data['list']:
                aqi_data = data['list'][0]
                return {
                    'aqi': aqi_data['main']['aqi'],
                    'co': aqi_data['components']['co'],
                    'no2': aqi_data['components']['no2'],
                    'o3': aqi_data['components']['o3'],
                    'pm2_5': aqi_data['components']['pm2_5'],
                    'pm10': aqi_data['components']['pm10'],
                    'timestamp': datetime.now().isoformat()
                }
            
            return {'error': 'No air quality data available'}
            
        except Exception as e:
            logger.error(f"Error fetching air quality data: {e}")
            return {'error': str(e)}
    
    def calculate_carbon_footprint(self, activity_type: str, amount: float, unit: str) -> Dict[str, Any]:
        """Calculate carbon footprint using Carbon Interface API"""
        try:
            url = f"{settings.CARBON_INTERFACE_API_BASE}/estimates"
            headers = {
                'Authorization': f'Bearer {settings.CARBON_INTERFACE_API_KEY}',
                'Content-Type': 'application/json'
            }
            
            # Map activity types to Carbon Interface format
            activity_mapping = {
                'electricity': {
                    'type': 'electricity',
                    'electricity_unit': 'kwh',
                    'electricity_value': amount,
                    'country': 'us'  # Default to US, should be configurable
                },
                'vehicle': {
                    'type': 'vehicle',
                    'distance_unit': 'mi',
                    'distance_value': amount,
                    'vehicle_model_id': '7268a9b7-17e8-4c8d-acca-57059252afe9'  # Average car
                },
                'flight': {
                    'type': 'flight',
                    'passengers': 1,
                    'legs': [
                        {
                            'departure_airport': 'lax',  # Should be configurable
                            'destination_airport': 'jfk',
                            'cabin_class': 'economy'
                        }
                    ]
                }
            }
            
            if activity_type not in activity_mapping:
                return {'error': f'Unsupported activity type: {activity_type}'}
            
            payload = activity_mapping[activity_type]
            
            response = self.session.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'carbon_kg': data['data']['attributes']['carbon_kg'],
                'carbon_lb': data['data']['attributes']['carbon_lb'],
                'carbon_mt': data['data']['attributes']['carbon_mt'],
                'activity_type': activity_type,
                'amount': amount,
                'unit': unit,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating carbon footprint: {e}")
            # Provide fallback estimates
            return self._get_fallback_carbon_estimate(activity_type, amount, unit)
    
    def _get_fallback_carbon_estimate(self, activity_type: str, amount: float, unit: str) -> Dict[str, Any]:
        """Provide fallback carbon estimates when API is unavailable"""
        # Simplified emission factors (kg CO2 per unit)
        emission_factors = {
            'electricity': 0.4,  # kg CO2 per kWh (US average)
            'gasoline': 2.3,     # kg CO2 per liter
            'natural_gas': 2.0,  # kg CO2 per cubic meter
            'vehicle_mile': 0.4, # kg CO2 per mile (average car)
            'flight_mile': 0.2   # kg CO2 per mile (economy class)
        }
        
        factor = emission_factors.get(activity_type, 0.1)
        carbon_kg = amount * factor
        
        return {
            'carbon_kg': carbon_kg,
            'carbon_lb': carbon_kg * 2.20462,
            'carbon_mt': carbon_kg / 1000,
            'activity_type': activity_type,
            'amount': amount,
            'unit': unit,
            'timestamp': datetime.now().isoformat(),
            'note': 'Estimated using fallback calculation'
        }
    
    def get_renewable_energy_data(self, location: str) -> Dict[str, Any]:
        """Fetch renewable energy potential data"""
        try:
            # This is a simplified implementation
            # In production, you would use NASA POWER API or similar
            
            # Mock data based on location (simplified)
            renewable_data = {
                'solar_potential': {
                    'daily_kwh_per_kw': 4.5,  # Average for US
                    'annual_kwh_per_kw': 1642,
                    'peak_sun_hours': 4.5
                },
                'wind_potential': {
                    'average_speed_ms': 6.5,
                    'capacity_factor': 0.35,
                    'annual_energy_density': 400  # kWh/m²/year
                },
                'location': location,
                'timestamp': datetime.now().isoformat()
            }
            
            return renewable_data
            
        except Exception as e:
            logger.error(f"Error fetching renewable energy data: {e}")
            return {'error': str(e), 'location': location}
    
    def get_climate_indicators(self, country_code: str = 'US') -> Dict[str, Any]:
        """Fetch climate indicators from World Bank API"""
        try:
            # World Bank Climate Change Knowledge Portal indicators
            indicators = [
                'EN.ATM.CO2E.PC',  # CO2 emissions per capita
                'EG.USE.ELEC.KH.PC',  # Electric power consumption per capita
                'AG.LND.FRST.ZS'   # Forest area (% of land area)
            ]
            
            climate_data = {}
            
            for indicator in indicators:
                url = f"{settings.WORLD_BANK_API_BASE}/country/{country_code}/indicator/{indicator}"
                params = {
                    'format': 'json',
                    'date': '2020:2022',  # Recent years
                    'per_page': 10
                }
                
                response = self.session.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if len(data) > 1 and data[1]:
                    latest_data = data[1][0]  # Most recent data point
                    climate_data[indicator] = {
                        'value': latest_data.get('value'),
                        'date': latest_data.get('date'),
                        'country': latest_data.get('country', {}).get('value')
                    }
            
            return {
                'country_code': country_code,
                'indicators': climate_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error fetching climate indicators: {e}")
            return {'error': str(e), 'country_code': country_code}
    
    def get_sdg_data(self, goal: int = 13) -> Dict[str, Any]:
        """Fetch UN SDG data (Goal 13: Climate Action)"""
        try:
            # Simplified SDG data - in production, use actual UN SDG API
            sdg_data = {
                'goal': goal,
                'title': 'Climate Action',
                'targets': [
                    {
                        'target': '13.1',
                        'description': 'Strengthen resilience and adaptive capacity to climate-related hazards',
                        'indicators': [
                            {
                                'indicator': '13.1.1',
                                'description': 'Number of deaths, missing persons and directly affected persons attributed to disasters per 100,000 population'
                            }
                        ]
                    },
                    {
                        'target': '13.2',
                        'description': 'Integrate climate change measures into national policies, strategies and planning',
                        'indicators': [
                            {
                                'indicator': '13.2.1',
                                'description': 'Number of countries that have communicated the establishment or operationalization of an integrated policy/strategy/plan'
                            }
                        ]
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }
            
            return sdg_data
            
        except Exception as e:
            logger.error(f"Error fetching SDG data: {e}")
            return {'error': str(e), 'goal': goal}
    
    def get_location_coordinates(self, location: str) -> Optional[Dict[str, float]]:
        """Get coordinates for a location using OpenWeatherMap geocoding"""
        try:
            url = f"http://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': settings.OPENWEATHER_API_KEY
            }
            
            response = self.session.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data:
                return {
                    'lat': data[0]['lat'],
                    'lon': data[0]['lon'],
                    'name': data[0]['name'],
                    'country': data[0]['country']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting coordinates for {location}: {e}")
            return None