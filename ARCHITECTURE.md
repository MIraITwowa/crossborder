# Technical Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│  Web Browser (Chrome, Safari, Firefox)                          │
│  - WebXR for AR Experience                                       │
│  - REST API Client                                               │
│  - 3D Model Viewer (Three.js / model-viewer)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTPS
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                      API GATEWAY                                 │
├─────────────────────────────────────────────────────────────────┤
│  Nginx (Production)                                              │
│  - Load Balancing                                                │
│  - SSL Termination                                               │
│  - Static File Serving                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  APPLICATION LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  Django + DRF (Gunicorn Workers)                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Apps:                                                    │  │
│  │  - users        (VIP System)                             │  │
│  │  - products     (Catalog + Dynamic Pricing)              │  │
│  │  - blockchain   (NFT Integration)                        │  │
│  │  - ar_experience (AR Sessions)                           │  │
│  │  - recommendations (AI Engine)                           │  │
│  │  - orders       (Priority Queue)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└────┬───────────┬────────────┬───────────┬──────────────────────┘
     │           │            │           │
     │           │            │           │
┌────▼─────┐ ┌──▼──────┐ ┌──▼────────┐ ┌▼──────────────────────┐
│ Database │ │  Redis  │ │  Celery   │ │      Kafka            │
│          │ │         │ │           │ │                        │
│ PostgreSQL│ │ Cache   │ │  Workers  │ │  Event Streaming     │
│          │ │ Session │ │  + Beat   │ │                        │
└──────────┘ └─────────┘ └───────────┘ └────────────────────────┘
```

## Data Flow Diagrams

### 1. AR Try-On Flow

```
User                Frontend            API Server          Celery           Database
 │                     │                    │                 │                 │
 │──Start AR Session──▶│                    │                 │                 │
 │                     │──POST /ar-sessions/start_session/──▶│                 │
 │                     │                    │─Create Session─▶│                 │
 │                     │                    │                 │◀─Save Session──│
 │                     │◀───Session ID──────│                 │                 │
 │◀───3D Model Data────│                    │                 │                 │
 │                     │                    │                 │                 │
 │──User Interacts─────▶                    │                 │                 │
 │ (Rotate/Zoom)       │                    │                 │                 │
 │                     │                    │                 │                 │
 │──End Session────────▶                    │                 │                 │
 │                     │──POST /ar-sessions/{id}/end_session/│                 │
 │                     │                    │─Update Session─▶│                 │
 │                     │                    │                 │◀─Save Metrics──│
 │                     │                    │─Track Interaction────────────────▶│
 │                     │                    │  (UserInteraction)                │
 │                     │                    │                 │                 │
 │                     │                    │  Generate Recommendations         │
 │                     │                    │  (Async Task)──────────▶          │
```

### 2. NFT Certificate Minting Flow

```
Purchase          API Server         Celery Worker      Blockchain       Database
   │                  │                    │                 │               │
   │──Buy Product────▶│                    │                 │               │
   │                  │─Create Order──────▶│                 │               │
   │                  │                    │                 │               │
   │                  │─Create NFT Cert───▶│                 │               │
   │                  │  (Status: PENDING) │                 │               │
   │                  │                    │                 │               │
   │                  │─Queue Mint Task────▶                 │               │
   │◀─Order Confirmed─│                    │                 │               │
   │                  │                    │                 │               │
   │                  │                    │──Mint NFT──────▶│               │
   │                  │                    │                 │               │
   │                  │                    │◀─Tx Hash────────│               │
   │                  │                    │                 │               │
   │                  │                    │─Update Status──────────────────▶│
   │                  │                    │  (Status: MINTED)               │
   │                  │                    │                 │               │
   │                  │                    │─Create Tx Record────────────────▶│
   │                  │                    │                 │               │
   │──NFT Certificate─│◀─Notify User───────│                 │               │
```

### 3. Dynamic Pricing Flow

```
Celery Beat     Celery Worker        Database         Kafka           Price History
     │                │                  │               │                  │
     │──Trigger──────▶│                  │               │                  │
     │   (Every 5min) │                  │               │                  │
     │                │                  │               │                  │
     │                │──Get Products────▶               │                  │
     │                │   (Limited Ed.)  │               │                  │
     │                │                  │               │                  │
     │                │◀─Product List────│               │                  │
     │                │                  │               │                  │
     │                │  For each product:               │                  │
     │                │  1. Calculate Demand Score       │                  │
     │                │     (views + AR tries * 3)       │                  │
     │                │                  │               │                  │
     │                │  2. Get Stock Level              │                  │
     │                │                  │               │                  │
     │                │  3. Compute New Price            │                  │
     │                │     (demand + stock factors)     │                  │
     │                │                  │               │                  │
     │                │──Update Price────▶               │                  │
     │                │                  │               │                  │
     │                │──Log Change──────────────────────────────────────▶  │
     │                │                  │               │                  │
     │                │──Publish Event───────────────────▶                  │
     │                │   (price-update) │               │                  │
```

### 4. VIP Priority Queue Flow

```
User               API Server          Priority Queue      Celery           Orders
 │                     │                      │               │               │
 │──Join Queue─────────▶                      │               │               │
 │  (Limited Product)  │                      │               │               │
 │                     │──Create Entry────────▶               │               │
 │                     │   priority_score     │               │               │
 │                     │   = user.vip_level   │               │               │
 │                     │                      │               │               │
 │◀─Queue Position─────│                      │               │               │
 │  (Priority: 1)      │                      │               │               │
 │                     │                      │               │               │
 │                     │      ┌──Scheduled Task (Every 5min)──┐              │
 │                     │      │               │               │              │
 │                     │      │  Process Queue by:            │              │
 │                     │      │  1. priority_score ASC        │              │
 │                     │      │  2. queued_at ASC             │              │
 │                     │      │                               │              │
 │                     │      │  PLATINUM (1) processes first │              │
 │                     │      │  GOLD (2) processes second    │              │
 │                     │      │  etc.                         │              │
 │                     │      │                               │              │
 │                     │      │  Create Order─────────────────────────────▶  │
 │                     │      │  Decrement Stock              │              │
 │                     │      │  Update Queue Status          │              │
 │                     │      └───────────────────────────────┘              │
 │                     │                      │               │               │
 │──Notification───────│◀─────────────────────────────────────               │
 │  (Order Created)    │                      │               │               │
```

### 5. AI Recommendation Generation

```
Scheduler       Feature Extractor    ML Engine        Database        User
    │                 │                  │               │              │
    │──Every 15min────▶                  │               │              │
    │                 │                  │               │              │
    │                 │──Get Interactions─▶              │              │
    │                 │                  │               │              │
    │                 │◀─Interaction Data─               │              │
    │                 │                  │               │              │
    │                 │──Aggregate Features              │              │
    │                 │  (views, AR, 3D)                 │              │
    │                 │                  │               │              │
    │                 │──Save Features───────────────────▶              │
    │                 │                  │               │              │
    │                 │                  │               │              │
    │──Daily at 2AM───────────────────▶  │               │              │
    │                 │                  │               │              │
    │                 │                  │──Get Features─▶              │
    │                 │                  │               │              │
    │                 │                  │◀─Feature Data─               │
    │                 │                  │               │              │
    │                 │                  │──Train Model──               │
    │                 │                  │  (Collaborative Filtering)   │
    │                 │                  │               │              │
    │                 │                  │──Generate Recs──────────────▶│
    │                 │                  │  (Top N products per user)   │
    │                 │                  │               │              │
    │                 │                  │               │              │
    │──API Request────────────────────────────────────────────────────▶ │
    │  GET /recommendations              │               │              │
    │                 │                  │               │              │
    │◀─Personalized Recommendations──────────────────────────────────── │
```

## Component Dependencies

```
┌───────────────────────────────────────────────────────────────┐
│                    External Dependencies                       │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Python 3.12+    PostgreSQL 15+    Redis 7+    Kafka 3.0+    │
│                                                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                    Core Framework                              │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Django 4.2+         Django REST Framework 3.14+             │
│  Celery 5.3+         Web3.py 6.0+                            │
│                                                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────┐
│                  Supporting Libraries                          │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  django-cors-headers     django-filter     django-redis       │
│  Pillow                  scikit-learn      pandas             │
│  kafka-python           gunicorn                              │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## Database Schema Overview

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│    User     │         │   Product    │         │  Category   │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ id          │         │ id           │         │ id          │
│ username    │         │ name         │─────────│ name        │
│ vip_level   │         │ brand        │         │ slug        │
│ wallet_addr │         │ base_price   │         │ parent      │
└──────┬──────┘         │ current_price│         └─────────────┘
       │                │ has_ar       │
       │                │ has_nft      │
       │                └──────┬───────┘
       │                       │
       │                       │
┌──────▼──────┐         ┌──────▼───────┐         ┌─────────────┐
│UserInteraction       │ NFTCertificate│         │ ARSession   │
├─────────────┤         ├──────────────┤         ├─────────────┤
│ user_id     │         │ product_id   │         │ user_id     │
│ product_id  │         │ owner_id     │         │ product_id  │
│ type        │         │ token_id     │         │ duration    │
│ duration    │         │ status       │         │ ar_data     │
└─────────────┘         │ minted_at    │         └─────────────┘
                        └──────────────┘
                        
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│PriorityQueue│         │    Order     │         │ PriceHistory│
├─────────────┤         ├──────────────┤         ├─────────────┤
│ user_id     │         │ user_id      │         │ product_id  │
│ product_id  │         │ total        │         │ old_price   │
│ priority    │         │ status       │         │ new_price   │
│ queue_pos   │         │ paid_at      │         │ demand_score│
│ expires_at  │         └──────────────┘         │ created_at  │
└─────────────┘                                   └─────────────┘
```

## Deployment Architecture (Docker)

```
┌────────────────────────────────────────────────────────────────┐
│                      Docker Compose                             │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │   Web    │  │  Celery  │  │  Celery  │  │   DB     │      │
│  │  Django  │  │  Worker  │  │   Beat   │  │PostgreSQL│      │
│  │  :8000   │  │          │  │          │  │  :5432   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │             │             │
│       └─────────────┴─────────────┴─────────────┘             │
│                           │                                    │
│                     ┌─────▼──────┐                            │
│                     │   Redis    │                            │
│                     │   :6379    │                            │
│                     └────────────┘                            │
│                           │                                    │
│                     ┌─────▼──────┐                            │
│                     │   Kafka    │                            │
│                     │   :9092    │                            │
│                     └────────────┘                            │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                      Security Layers                           │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Layer 1: Network Security                                     │
│  ─────────────────────────                                     │
│  - HTTPS/TLS                                                   │
│  - CORS Configuration                                          │
│  - Rate Limiting (Future)                                      │
│                                                                │
│  Layer 2: Authentication                                       │
│  ──────────────────────                                        │
│  - Session Authentication                                      │
│  - JWT Tokens (Ready)                                          │
│  - Password Hashing (Django)                                   │
│                                                                │
│  Layer 3: Authorization                                        │
│  ─────────────────────                                         │
│  - VIP Level Permissions                                       │
│  - Owner-based Access                                          │
│  - Staff/Admin Roles                                           │
│                                                                │
│  Layer 4: Data Security                                        │
│  ────────────────────                                          │
│  - SQL Injection Protected (ORM)                               │
│  - XSS Protection (Django)                                     │
│  - CSRF Protection                                             │
│                                                                │
│  Layer 5: Blockchain                                           │
│  ──────────────────                                            │
│  - Immutable NFT Records                                       │
│  - Cryptographic Signatures                                    │
│  - Ownership Verification                                      │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## Scalability Strategy

```
┌───────────────────────────────────────────────────────────────┐
│                   Horizontal Scaling                           │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Application Tier:                                             │
│  - Multiple Gunicorn workers                                   │
│  - Load balancer (Nginx)                                       │
│  - Stateless API design                                        │
│                                                                │
│  Worker Tier:                                                  │
│  - Multiple Celery workers                                     │
│  - Task routing by type                                        │
│  - Auto-scaling based on queue length                          │
│                                                                │
│  Database Tier:                                                │
│  - Read replicas                                               │
│  - Connection pooling                                          │
│  - Query optimization                                          │
│                                                                │
│  Cache Tier:                                                   │
│  - Redis Cluster                                               │
│  - Cache invalidation strategy                                 │
│  - Session storage                                             │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

---

*Architecture Documentation - Last Updated: December 23, 2025*
