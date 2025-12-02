from fastapi import FastAPI
from api_handler import FastAPIHandler
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram, Counter

app = FastAPI()
app.handler = FastAPIHandler()

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
    'Total number of errors (4xx and 5xx)',
    ['status_code']
)





@app.get('/')
def root_dir():
    return({'Hello': 'world'})

@app.post('/api/prediction')
def make_prediction(phone_id: int, item_features: dict):

    try:
        prediction = app.handler.predict(item_features)[0]
        
        prediction_histogram.observe(float(prediction))
        request_counter.labels(status='success').inc()
        
        
        return {
            'price': int(prediction),
            'phone_id': phone_id
        }
    except Exception as e:
        request_counter.labels(status='error').inc()
        error_counter.labels(status_code='500').inc()
        return {
            'error': str(e),
            'phone_id': phone_id
        }