from time import time
from fastapi import FastAPI, HTTPException
from api_handler import FastAPIHandler
from db_handler import DatabaseHandler
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram, Counter, Summary, Gauge
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Phone Price Prediction Service")
app.handler = FastAPIHandler()
app.db = DatabaseHandler()

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

prediction_histogram = Histogram(
    'model_prediction_distribution',
    'Distribution of model predictions (price ranges)',
    buckets=(0.9,1.9,2.9,3.9)
)

request_counter = Counter(
    'prediction_requests_total',
    'Total number of prediction requests',
    ['status']
)


error_counter = Counter(
    'prediction_errors_total',
    'Total number of errors',
    ['status_code', 'error_type']
)

db_write_counter = Counter(
    'database_writes_total',
    'Total number of database write operations',
    ['table', 'status']
)

prediction_latency = Summary(
    'prediction_latency_seconds',
    'Time spent processing prediction request'
)

db_operation_latency = Summary(
    'database_operation_latency_seconds',
    'Time spent on database operations',
    ['operation']
)

prediction_distribution_gauge = Gauge(
    'prediction_class_distribution',
    'Distribution of predicted classes',
    ['price_range']
)

total_predictions_gauge = Gauge(
    'total_predictions_count',
    'Total number of predictions in database'
)





@app.get('/')
def root_dir():
    return {
        'service': 'Phone Price Prediction',
        'status': 'active',
        'version': '4.0',
        'database': 'connected'
    }

@app.post('/api/prediction')
def make_prediction(phone_id: int, item_features: dict):

    start_time = time.time()

    try:
        prediction = app.handler.predict(item_features)[0]

        db_start = time.time()
        try:
            app.db.save_phone_data(phone_id, item_features)
            db_write_counter.labels(table='phones', status='success').inc()
            
            app.db.save_prediction(phone_id, int(prediction))
            db_write_counter.labels(table='predictions', status='success').inc()
            
            db_duration = time.time() - db_start
            db_operation_latency.labels(operation='write').observe(db_duration)
            
        except Exception as db_error:
            logger.error(f"Database error for phone_id {phone_id}: {db_error}")
            db_write_counter.labels(table='both', status='error').inc()
            error_counter.labels(status_code='500', error_type='database').inc()
        
        
        prediction_histogram.observe(float(prediction))
        request_counter.labels(status='success').inc()
        
        total_duration = time.time() - start_time
        prediction_latency.observe(total_duration)
        
        logger.info(f"Prediction for phone_id {phone_id}: {int(prediction)} (took {total_duration:.3f}s)")
        
        
        return {
            'price': int(prediction),
            'phone_id': phone_id,
            'processing_time': round(total_duration, 3)
        }
    
    except Exception as e:
        logger.error(f"Prediction error for phone_id {phone_id}: {e}")
        request_counter.labels(status='error').inc()
        error_counter.labels(status_code='500', error_type='prediction').inc()
        raise HTTPException(
            status_code=500, 
            detail=f"Prediction failed: {str(e)}"
        )
    

@app.get('/api/health')
def health_check():
    try:
        db_start = time.time()
        stats = app.db.get_prediction_stats(hours=1)
        db_duration = time.time() - db_start
        db_operation_latency.labels(operation='read').observe(db_duration)
        
        return {
            'status': 'healthy',
            'database': 'connected',
            'recent_predictions_1h': sum(s['count'] for s in stats),
            'db_query_time': round(db_duration, 3)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e)
        }

@app.get('/api/stats')
def get_statistics(hours: int = 24):
    try:
        return {
            'period_hours': hours,
            'feature_drift': app.db.get_feature_drift(hours),
            'predictions': app.db.get_prediction_stats(hours),
            'timeline': app.db.get_prediction_distribution_timeline(hours)
        }
    except Exception as e:
        logger.error(f"Statistics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))