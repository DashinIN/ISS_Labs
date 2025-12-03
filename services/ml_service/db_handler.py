import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseHandler:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'database'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'phone_predictions'),
            'user': os.getenv('DB_USER', 'admin'),
            'password': os.getenv('DB_PASSWORD', 'admin')
        }
        self._test_connection()
    
    def _test_connection(self):
        try:
            with self.get_connection() as conn:
                logger.info("Database connection successful")
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
    
    @contextmanager
    def get_connection(self):
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise e
        finally:
            if conn:
                conn.close()
    
    def save_phone_data(self, phone_id: int, features: dict):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO phones (
                        phone_id, battery_power, blue, clock_speed, dual_sim, 
                        fc, four_g, int_memory, m_dep, mobile_wt, n_cores, 
                        pc, px_height, px_width, ram, sc_h, sc_w, 
                        talk_time, three_g, touch_screen, wifi
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (phone_id) 
                    DO UPDATE SET
                        battery_power = EXCLUDED.battery_power,
                        ram = EXCLUDED.ram,
                        ts = CURRENT_TIMESTAMP
                    RETURNING id, ts
                """, (
                    phone_id,
                    features.get('battery_power'),
                    features.get('blue'),
                    features.get('clock_speed'),
                    features.get('dual_sim'),
                    features.get('fc'),
                    features.get('four_g'),
                    features.get('int_memory'),
                    features.get('m_dep'),
                    features.get('mobile_wt'),
                    features.get('n_cores'),
                    features.get('pc'),
                    features.get('px_height'),
                    features.get('px_width'),
                    features.get('ram'),
                    features.get('sc_h'),
                    features.get('sc_w'),
                    features.get('talk_time'),
                    features.get('three_g'),
                    features.get('touch_screen'),
                    features.get('wifi')
                ))
                result = cur.fetchone()
                return result
    
    def save_prediction(self, phone_id: int, prediction: int):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO predictions (phone_id, predicted_price_range)
                    VALUES (%s, %s)
                    RETURNING id, ts
                """, (phone_id, prediction))
                result = cur.fetchone()
                return result
    
    def get_prediction_stats(self, hours: int = 24):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        predicted_price_range,
                        COUNT(*) as count,
                        ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER () * 100, 2) as percentage
                    FROM predictions
                    WHERE ts > NOW() - INTERVAL '%s hours'
                    GROUP BY predicted_price_range
                    ORDER BY predicted_price_range
                """, (hours,))
                return cur.fetchall()
    
  
    
    def get_prediction_distribution_timeline(self, hours: int = 24):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT 
                        date_trunc('hour', ts) as hour,
                        predicted_price_range,
                        COUNT(*) as count
                    FROM predictions
                    WHERE ts > NOW() - INTERVAL '%s hours'
                    GROUP BY date_trunc('hour', ts), predicted_price_range
                    ORDER BY hour, predicted_price_range
                """, (hours,))
                return cur.fetchall()