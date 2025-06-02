"""
Impact tracking system for climate actions
"""
import logging
import sqlite3
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import os

logger = logging.getLogger(__name__)

class ImpactTracker:
    """Track and quantify environmental impact of climate actions"""
    
    def __init__(self, db_path: str = "data/impact_tracker.db"):
        self.db_path = db_path
        self._ensure_db_directory()
        self._initialize_database()
        
        # Impact calculation factors (kg CO2 equivalent)
        self.impact_factors = {
            'led_bulb_replacement': 0.5,  # kg CO2/year per bulb
            'thermostat_adjustment': 0.3,  # kg CO2/year per degree
            'car_trip_avoided': 0.4,      # kg CO2 per mile
            'public_transport_use': -0.3,  # negative = reduction per mile
            'bike_trip': -0.4,            # kg CO2 saved per mile
            'solar_panel_kwh': -0.4,      # kg CO2 saved per kWh
            'energy_efficient_appliance': 2.0,  # kg CO2/year saved
            'tree_planted': -22.0,        # kg CO2 absorbed per year per tree
            'composting': -0.5,           # kg CO2/year per household
            'meat_free_meal': -0.9,       # kg CO2 saved per meal
            'local_food_purchase': -0.2,  # kg CO2 saved per meal
            'water_conservation': 0.1,    # kg CO2/year per gallon saved daily
            'recycling': -0.3,            # kg CO2 saved per kg recycled
            'renewable_energy_switch': -3.6,  # kg CO2/year per household
            'insulation_upgrade': -2.3,   # kg CO2/year per household
            'electric_vehicle': -2400,    # kg CO2/year vs gas car
        }
    
    def _ensure_db_directory(self):
        """Ensure the database directory exists"""
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self):
        """Initialize SQLite database for impact tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create actions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS actions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        action_type TEXT NOT NULL,
                        description TEXT,
                        quantity REAL,
                        unit TEXT,
                        co2_impact REAL,
                        energy_impact REAL,
                        water_impact REAL,
                        waste_impact REAL,
                        location TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        verified BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Create user_metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        metric_type TEXT,
                        value REAL,
                        unit TEXT,
                        period_start DATE,
                        period_end DATE,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create goals table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS goals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT,
                        goal_type TEXT,
                        target_value REAL,
                        current_value REAL DEFAULT 0,
                        unit TEXT,
                        deadline DATE,
                        status TEXT DEFAULT 'active',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Impact tracking database initialized")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def track_action(self, user_id: str, action_type: str, quantity: float = 1.0, 
                    unit: str = "unit", location: str = None, description: str = None) -> Dict[str, Any]:
        """Track a specific climate action and calculate its impact"""
        try:
            # Calculate environmental impact
            impact = self._calculate_impact(action_type, quantity, location)
            
            # Store action in database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO actions 
                    (user_id, action_type, description, quantity, unit, co2_impact, 
                     energy_impact, water_impact, waste_impact, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, action_type, description, quantity, unit,
                    impact['co2_impact'], impact['energy_impact'], 
                    impact['water_impact'], impact['waste_impact'], location
                ))
                
                action_id = cursor.lastrowid
                conn.commit()
            
            # Update user metrics
            self._update_user_metrics(user_id, impact)
            
            result = {
                'action_id': action_id,
                'action_type': action_type,
                'quantity': quantity,
                'unit': unit,
                'impact': impact,
                'timestamp': datetime.now().isoformat(),
                'message': self._generate_impact_message(action_type, impact)
            }
            
            logger.info(f"Tracked action {action_type} for user {user_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error tracking action: {e}")
            return {'error': str(e)}
    
    def _calculate_impact(self, action_type: str, quantity: float, location: str = None) -> Dict[str, float]:
        """Calculate environmental impact of an action"""
        base_factor = self.impact_factors.get(action_type, 0.0)
        
        # Calculate CO2 impact
        co2_impact = base_factor * quantity
        
        # Estimate other impacts based on action type
        energy_impact = 0.0
        water_impact = 0.0
        waste_impact = 0.0
        
        if 'energy' in action_type or 'solar' in action_type or 'led' in action_type:
            energy_impact = abs(co2_impact) * 2.5  # kWh equivalent
        
        if 'water' in action_type or 'conservation' in action_type:
            water_impact = quantity * 10  # gallons saved
        
        if 'recycling' in action_type or 'composting' in action_type:
            waste_impact = quantity * 0.5  # kg waste diverted
        
        return {
            'co2_impact': round(co2_impact, 3),
            'energy_impact': round(energy_impact, 3),
            'water_impact': round(water_impact, 3),
            'waste_impact': round(waste_impact, 3)
        }
    
    def _update_user_metrics(self, user_id: str, impact: Dict[str, float]):
        """Update cumulative user metrics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get current period (this month)
                now = datetime.now()
                period_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                period_end = (period_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                for metric_type, value in impact.items():
                    if value != 0:
                        # Check if metric exists for this period
                        cursor.execute('''
                            SELECT id, value FROM user_metrics 
                            WHERE user_id = ? AND metric_type = ? 
                            AND period_start = ? AND period_end = ?
                        ''', (user_id, metric_type, period_start.date(), period_end.date()))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Update existing metric
                            new_value = existing[1] + value
                            cursor.execute('''
                                UPDATE user_metrics SET value = ? WHERE id = ?
                            ''', (new_value, existing[0]))
                        else:
                            # Create new metric
                            cursor.execute('''
                                INSERT INTO user_metrics 
                                (user_id, metric_type, value, unit, period_start, period_end)
                                VALUES (?, ?, ?, ?, ?, ?)
                            ''', (user_id, metric_type, value, 'kg', period_start.date(), period_end.date()))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error updating user metrics: {e}")
    
    def get_user_impact_summary(self, user_id: str, period_days: int = 30) -> Dict[str, Any]:
        """Get user's impact summary for a specified period"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period_days)
                
                # Get actions in period
                cursor.execute('''
                    SELECT action_type, COUNT(*) as count, 
                           SUM(co2_impact) as total_co2,
                           SUM(energy_impact) as total_energy,
                           SUM(water_impact) as total_water,
                           SUM(waste_impact) as total_waste
                    FROM actions 
                    WHERE user_id = ? AND timestamp >= ?
                    GROUP BY action_type
                    ORDER BY total_co2 DESC
                ''', (user_id, start_date))
                
                actions_summary = []
                total_impact = {'co2': 0, 'energy': 0, 'water': 0, 'waste': 0}
                
                for row in cursor.fetchall():
                    action_data = {
                        'action_type': row[0],
                        'count': row[1],
                        'co2_impact': round(row[2] or 0, 3),
                        'energy_impact': round(row[3] or 0, 3),
                        'water_impact': round(row[4] or 0, 3),
                        'waste_impact': round(row[5] or 0, 3)
                    }
                    actions_summary.append(action_data)
                    
                    total_impact['co2'] += action_data['co2_impact']
                    total_impact['energy'] += action_data['energy_impact']
                    total_impact['water'] += action_data['water_impact']
                    total_impact['waste'] += action_data['waste_impact']
                
                # Get total action count
                cursor.execute('''
                    SELECT COUNT(*) FROM actions 
                    WHERE user_id = ? AND timestamp >= ?
                ''', (user_id, start_date))
                
                total_actions = cursor.fetchone()[0]
                
                return {
                    'user_id': user_id,
                    'period_days': period_days,
                    'total_actions': total_actions,
                    'total_impact': {
                        'co2_saved_kg': round(abs(total_impact['co2']), 3),
                        'energy_saved_kwh': round(total_impact['energy'], 3),
                        'water_saved_gallons': round(total_impact['water'], 3),
                        'waste_diverted_kg': round(total_impact['waste'], 3)
                    },
                    'actions_breakdown': actions_summary,
                    'equivalent_impact': self._calculate_equivalents(total_impact['co2']),
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting user impact summary: {e}")
            return {'error': str(e)}
    
    def _calculate_equivalents(self, co2_kg: float) -> Dict[str, Any]:
        """Calculate equivalent impacts for better understanding"""
        co2_kg = abs(co2_kg)  # Use absolute value for equivalents
        
        return {
            'trees_equivalent': round(co2_kg / 22, 1),  # Trees needed to absorb this CO2
            'car_miles_avoided': round(co2_kg / 0.4, 1),  # Miles of driving avoided
            'lightbulb_hours': round(co2_kg / 0.0005, 0),  # Hours of LED bulb use
            'smartphone_charges': round(co2_kg / 0.008, 0),  # Smartphone charges
            'plastic_bottles_recycled': round(co2_kg / 0.03, 0)  # Plastic bottles recycled
        }
    
    def _generate_impact_message(self, action_type: str, impact: Dict[str, float]) -> str:
        """Generate encouraging message about the impact"""
        co2_impact = abs(impact['co2_impact'])
        
        if co2_impact == 0:
            return f"Great job taking action with {action_type}! Every action counts."
        
        if co2_impact < 1:
            return f"Nice! Your {action_type} saved {co2_impact:.2f} kg of CO2. That's like avoiding {co2_impact/0.4:.1f} miles of driving!"
        elif co2_impact < 10:
            return f"Excellent! Your {action_type} saved {co2_impact:.1f} kg of CO2. That's equivalent to planting {co2_impact/22:.1f} trees!"
        else:
            return f"Amazing impact! Your {action_type} saved {co2_impact:.1f} kg of CO2. That's like taking a car off the road for {co2_impact/0.4:.0f} miles!"
    
    def set_user_goal(self, user_id: str, goal_type: str, target_value: float, 
                     unit: str, deadline: str) -> Dict[str, Any]:
        """Set a climate action goal for a user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO goals (user_id, goal_type, target_value, unit, deadline)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, goal_type, target_value, unit, deadline))
                
                goal_id = cursor.lastrowid
                conn.commit()
            
            return {
                'goal_id': goal_id,
                'user_id': user_id,
                'goal_type': goal_type,
                'target_value': target_value,
                'unit': unit,
                'deadline': deadline,
                'status': 'active'
            }
            
        except Exception as e:
            logger.error(f"Error setting user goal: {e}")
            return {'error': str(e)}
    
    def get_user_goals_progress(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's goals and their progress"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get active goals
                cursor.execute('''
                    SELECT id, goal_type, target_value, current_value, unit, deadline, status
                    FROM goals WHERE user_id = ? AND status = 'active'
                ''', (user_id,))
                
                goals = []
                for row in cursor.fetchall():
                    goal = {
                        'goal_id': row[0],
                        'goal_type': row[1],
                        'target_value': row[2],
                        'current_value': row[3],
                        'unit': row[4],
                        'deadline': row[5],
                        'status': row[6],
                        'progress_percentage': round((row[3] / row[2]) * 100, 1) if row[2] > 0 else 0
                    }
                    goals.append(goal)
                
                return goals
                
        except Exception as e:
            logger.error(f"Error getting user goals: {e}")
            return []