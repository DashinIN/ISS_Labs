import requests
import time
import random
import logging


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

time.sleep(10)


def send_prediction_request(phone_id):
    """Отправка одного запроса на предсказание"""
    params = {'phone_id': phone_id}
    data = {
        "battery_power": random.randint(500, 1999),
        "blue": random.randint(0, 1),
        "clock_speed": round(random.uniform(0.5, 3.0), 1),
        "dual_sim": random.randint(0, 1),
        "fc": random.randint(0, 19),
        "four_g": random.randint(0, 1),
        "int_memory": random.randint(2, 64),
        "m_dep": round(random.uniform(0.1, 1.0), 1),
        "mobile_wt": random.randint(80, 200),
        "n_cores": random.randint(1, 8),
        "pc": random.randint(0, 20),
        "px_height": random.randint(0, 1907),
        "px_width": random.randint(501, 1988),
        "ram": random.randint(263, 3989),
        "sc_h": random.randint(5, 19),
        "sc_w": random.randint(0, 18),
        "talk_time": random.randint(2, 20),
        "three_g": random.randint(0, 1),
        "touch_screen": random.randint(0, 1),
        "wifi": random.randint(0, 1)
    }
    
    try:
        response = requests.post(
            'http://phone-predict:8000/api/prediction',
            params=params,
            json=data,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Phone ID {phone_id}: {result}")
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed for phone_id {phone_id}: {e}")
        return None


def main():
    logger.info("Starting request generator...")
    
    phone_id = 0
    while True:
        send_prediction_request(phone_id)
        phone_id += 1
        
        sleep_time = random.randint(1, 5)
        time.sleep(sleep_time)



if __name__ == "__main__":
    main()
