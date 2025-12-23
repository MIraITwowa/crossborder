# API Documentation

## Base URL
```
http://localhost:8000/api/
```

## Authentication
Currently uses Django session authentication. JWT can be configured by uncommenting the JWT settings in `settings.py`.

## API Endpoints

### Users

#### List Users
```
GET /api/users/
```

#### Get User Details
```
GET /api/users/{id}/
```

#### Get User VIP Status
```
GET /api/users/{id}/vip_status/
```
Response:
```json
{
  "vip_level": "GOLD",
  "priority_score": 2,
  "benefits": {
    "priority_queue_access": true,
    "early_access": true,
    "exclusive_products": false
  }
}
```

#### Get User Interactions
```
GET /api/users/{id}/interactions/
```

### Products

#### List Products
```
GET /api/products/
```
Query Parameters:
- `category`: Filter by category ID
- `brand`: Filter by brand name
- `product_type`: Filter by product type
- `is_limited_edition`: Filter limited edition products
- `has_ar_support`: Filter products with AR support
- `search`: Search in name, description, brand
- `ordering`: Order by `current_price`, `created_at`, `name`

#### Get Product Details
```
GET /api/products/{slug}/
```

#### Get Product AR Model
```
GET /api/products/{slug}/ar_model/
```
Response:
```json
{
  "has_ar_support": true,
  "model_file": "http://localhost:8000/media/ar_models/watch.glb",
  "thumbnail": "http://localhost:8000/media/product_thumbnails/watch.jpg"
}
```

#### Get Product NFT Information
```
GET /api/products/{slug}/nft_info/
```
Response:
```json
{
  "has_nft_certificate": true,
  "contract_address": "0x1234...",
  "token_id": "12345"
}
```

#### Get Product Price History
```
GET /api/products/{slug}/price_history/
```

#### Get Featured Products
```
GET /api/products/featured/
```

#### Get Limited Edition Products
```
GET /api/products/limited_edition/
```

### Categories

#### List Categories
```
GET /api/categories/
```

#### Get Category Details
```
GET /api/categories/{slug}/
```

### AR Experience

#### Start AR Session
```
POST /api/ar-sessions/start_session/
```
Request Body:
```json
{
  "product_id": 1,
  "device_type": "mobile",
  "browser": "Chrome"
}
```

#### End AR Session
```
POST /api/ar-sessions/{id}/end_session/
```
Request Body:
```json
{
  "screenshots_taken": 3,
  "rotation_count": 15,
  "zoom_count": 5,
  "ar_data": {
    "measurements": {...}
  }
}
```

#### Update Session Metrics
```
POST /api/ar-sessions/{id}/update_metrics/
```
Request Body:
```json
{
  "screenshots_taken": 2,
  "rotation_count": 10,
  "zoom_count": 3
}
```

#### List AR Models
```
GET /api/ar-models/?product_id={product_id}
```

### User Interactions

#### Create Interaction
```
POST /api/interactions/
```
Request Body:
```json
{
  "product": 1,
  "interaction_type": "VIEW",
  "duration_seconds": 30,
  "metadata": {
    "source": "search"
  }
}
```

Interaction Types:
- `VIEW`: Product view
- `AR_TRY`: AR try-on
- `3D_ROTATE`: 3D model rotation
- `ZOOM`: Zoom on model
- `SAVE`: Save to wishlist
- `SHARE`: Share product

#### List User's Interactions
```
GET /api/interactions/
```

## Response Format

### Success Response
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": "Error message"
}
```

## Rate Limiting
No rate limiting currently configured. Consider adding in production.

## CORS
CORS is enabled for `localhost:3000` and `localhost:8000` in development.

## Pagination
Default page size: 20 items per page
Use `?page=2` for pagination

## Filtering Examples

### Get all Rolex watches with AR support
```
GET /api/products/?brand=Rolex&product_type=WATCH&has_ar_support=true
```

### Search for products
```
GET /api/products/?search=luxury+watch
```

### Get products sorted by price (ascending)
```
GET /api/products/?ordering=current_price
```

### Get products sorted by price (descending)
```
GET /api/products/?ordering=-current_price
```

## Celery Tasks

### Scheduled Tasks (via Celery Beat)

1. **Update Product Pricing** - Every 5 minutes
   - Adjusts prices based on demand and inventory
   - Task: `products.tasks.update_product_pricing`

2. **Update Interaction Features** - Every 15 minutes
   - Aggregates user interactions for ML
   - Task: `recommendations.tasks.update_interaction_features`

3. **Expire Queue Entries** - Every 5 minutes
   - Marks expired priority queue entries
   - Task: `orders.tasks.expire_queue_entries`

4. **Train Recommendation Model** - Daily at 2 AM
   - Trains/updates recommendation model
   - Task: `recommendations.tasks.train_recommendation_model`

### Manual Tasks

1. **Generate User Recommendations**
```python
from recommendations.tasks import generate_user_recommendations
generate_user_recommendations.delay(user_id=1)
```

2. **Mint NFT Certificate**
```python
from blockchain.tasks import mint_nft_certificate
mint_nft_certificate.delay(certificate_id=1)
```

3. **Process Priority Queue**
```python
from orders.tasks import process_priority_queue
process_priority_queue.delay(product_id=1)
```
