# AI Chatbot - Technical Specification

## Assumptions
- Multi-user chatbot with conversation history persistence
- Integration with external AI/LLM API (OpenAI, Anthropic, or similar)
- RESTful API for frontend integration
- PostgreSQL/MySQL for data persistence
- Redis for session management and caching
- Asynchronous message processing for scalability
- JWT-based authentication
- Support for multiple conversation contexts per user

## API Endpoints

### 1. User Authentication
**POST /api/v1/auth/register**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}

Response (201):
{
  "user_id": "uuid-string",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-01-07T10:30:00Z"
}
```

**POST /api/v1/auth/login**
```json
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "jwt-token-string",
  "refresh_token": "refresh-token-string",
  "expires_in": 3600,
  "user_id": "uuid-string"
}
```

### 2. Conversation Management
**POST /api/v1/conversations**
```json
Request:
{
  "title": "Help with Python",
  "context": "programming"
}

Response (201):
{
  "conversation_id": "uuid-string",
  "title": "Help with Python",
  "context": "programming",
  "created_at": "2026-01-07T10:30:00Z",
  "user_id": "uuid-string"
}
```

**GET /api/v1/conversations**
```json
Response (200):
{
  "conversations": [
    {
      "conversation_id": "uuid-string",
      "title": "Help with Python",
      "last_message": "How do I use decorators?",
      "updated_at": "2026-01-07T10:30:00Z",
      "message_count": 5
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20
}
```

**GET /api/v1/conversations/{conversation_id}**
```json
Response (200):
{
  "conversation_id": "uuid-string",
  "title": "Help with Python",
  "context": "programming",
  "created_at": "2026-01-07T10:30:00Z",
  "messages": [
    {
      "message_id": "uuid-string",
      "role": "user",
      "content": "How do I use decorators?",
      "timestamp": "2026-01-07T10:30:00Z"
    },
    {
      "message_id": "uuid-string",
      "role": "assistant",
      "content": "Decorators are functions that...",
      "timestamp": "2026-01-07T10:30:05Z"
    }
  ]
}
```

**DELETE /api/v1/conversations/{conversation_id}**
```json
Response (204): No Content
```

### 3. Chat Messages
**POST /api/v1/conversations/{conversation_id}/messages**
```json
Request:
{
  "content": "How do I use decorators in Python?",
  "stream": false
}

Response (200):
{
  "message_id": "uuid-string",
  "conversation_id": "uuid-string",
  "user_message": {
    "message_id": "uuid-string",
    "role": "user",
    "content": "How do I use decorators in Python?",
    "timestamp": "2026-01-07T10:30:00Z"
  },
  "assistant_message": {
    "message_id": "uuid-string",
    "role": "assistant",
    "content": "Decorators are functions that modify...",
    "timestamp": "2026-01-07T10:30:05Z"
  },
  "tokens_used": 250,
  "latency_ms": 1200
}
```

**POST /api/v1/conversations/{conversation_id}/messages/stream**
```json
Request:
{
  "content": "Explain async/await",
  "stream": true
}

Response (200): Server-Sent Events (SSE)
data: {"type": "start", "message_id": "uuid-string"}
data: {"type": "chunk", "content": "Async"}
data: {"type": "chunk", "content": "/await"}
data: {"type": "chunk", "content": " allows"}
data: {"type": "end", "tokens_used": 150}
```

### 4. Health & Metrics
**GET /api/v1/health**
```json
Response (200):
{
  "status": "healthy",
  "database": "connected",
  "cache": "connected",
  "ai_service": "available",
  "timestamp": "2026-01-07T10:30:00Z"
}
```

## Data Model

### Users Table
```sql
users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_active BOOLEAN DEFAULT TRUE,
  last_login TIMESTAMP,
  INDEX idx_email (email)
)
```

### Conversations Table
```sql
conversations (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  context VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  is_deleted BOOLEAN DEFAULT FALSE,
  INDEX idx_user_id (user_id),
  INDEX idx_updated_at (updated_at)
)
```

### Messages Table
```sql
messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  tokens_used INTEGER,
  created_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  INDEX idx_conversation_id (conversation_id),
  INDEX idx_created_at (created_at)
)
```

### API Keys Table (for AI service tracking)
```sql
api_usage (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  tokens_used INTEGER NOT NULL,
  request_type VARCHAR(50),
  cost_usd DECIMAL(10, 6),
  created_at TIMESTAMP DEFAULT NOW(),
  INDEX idx_user_id_date (user_id, created_at)
)
```

## Validation Rules

### User Registration
- Email: Valid email format, max 255 chars, unique
- Password: Min 8 chars, must include uppercase, lowercase, number, special char
- Name: 2-255 chars, alphanumeric + spaces

### Conversations
- Title: 1-500 chars, required
- Context: Optional, max 100 chars, alphanumeric

### Messages
- Content: 1-10,000 chars for user messages
- Role: Must be one of ['user', 'assistant', 'system']
- Conversation must exist and belong to authenticated user

### Rate Limiting
- 100 requests/minute per user for standard messages
- 20 requests/minute for streaming messages
- 1000 requests/day per user

## Error Codes

| Code     | HTTP Status | Description                   |
| -------- | ----------- | ----------------------------- |
| AUTH_001 | 401         | Invalid credentials           |
| AUTH_002 | 401         | Token expired                 |
| AUTH_003 | 403         | Insufficient permissions      |
| VAL_001  | 400         | Invalid email format          |
| VAL_002  | 400         | Password requirements not met |
| VAL_003  | 400         | Message content too long      |
| VAL_004  | 400         | Invalid conversation ID       |
| RES_001  | 404         | Conversation not found        |
| RES_002  | 404         | User not found                |
| RATE_001 | 429         | Rate limit exceeded           |
| AI_001   | 503         | AI service unavailable        |
| AI_002   | 500         | AI processing error           |
| SYS_001  | 500         | Database connection error     |
| SYS_002  | 500         | Internal server error         |

## Edge Cases

1. **Concurrent Message Sending**
   - Use optimistic locking with version numbers
   - Queue messages for same conversation
   - Return 409 Conflict if race condition detected

2. **Long-Running AI Responses**
   - Implement 30s timeout for AI calls
   - Return partial response with timeout indicator
   - Allow retry mechanism

3. **Conversation Deletion During Active Chat**
   - Soft delete conversations
   - Check conversation exists before each message
   - Return 410 Gone if conversation deleted

4. **Token Limit Exceeded**
   - Truncate conversation history if context too large
   - Keep last N messages + system prompt
   - Notify user of truncation

5. **Network Interruption During Streaming**
   - Implement heartbeat mechanism
   - Store partial responses
   - Allow resume from last checkpoint

6. **Duplicate Message Submission**
   - Implement idempotency keys
   - Cache recent message hashes (5 min TTL)
   - Return existing response for duplicates

## Non-Functional Requirements

### Latency
- **Target Response Time:**
  - Standard messages: < 2s (p95)
  - Streaming first token: < 500ms (p95)
  - API authentication: < 100ms (p95)
  - Conversation history: < 200ms (p95)

- **Optimization Strategies:**
  - Cache frequently accessed conversations (Redis)
  - Connection pooling for database
  - Async/await for AI API calls
  - CDN for static assets

### Logging

**Log Levels:**
- INFO: All API requests/responses (excluding sensitive data)
- WARN: Rate limit hits, slow queries, retry attempts
- ERROR: Failed AI calls, database errors, authentication failures
- DEBUG: Detailed request tracing (dev/staging only)

**Logged Fields:**
- Request ID (UUID for tracing)
- User ID
- Endpoint
- Response time
- Status code
- Error details (if applicable)
- Tokens used
- Timestamp (ISO 8601)

**Log Storage:**
- Centralized logging (ELK stack or CloudWatch)
- Retention: 30 days for INFO, 90 days for ERROR
- Real-time alerting for ERROR threshold breaches

### Security

**Authentication & Authorization:**
- JWT tokens with 1-hour expiration
- Refresh tokens with 30-day expiration
- HTTPS only (TLS 1.3)
- API key rotation every 90 days

**Data Protection:**
- Passwords: bcrypt with cost factor 12
- Sensitive data encryption at rest (AES-256)
- PII data anonymization in logs
- SQL injection prevention (parameterized queries)
- XSS prevention (input sanitization)
- CSRF tokens for state-changing operations

**Infrastructure Security:**
- WAF (Web Application Firewall)
- DDoS protection
- Network segmentation (private subnets)
- Regular security audits
- Dependency vulnerability scanning

**Compliance:**
- GDPR compliance (data export/deletion)
- User consent for data processing
- Cookie policy
- Privacy policy disclosure

### Scalability
- Horizontal scaling: Load balancer with auto-scaling groups
- Database: Read replicas for conversation history
- Caching: Redis cluster for sessions and frequent queries
- Message queue: RabbitMQ/Kafka for async processing
- CDN: Static assets and API responses (where appropriate)

### Monitoring & Alerting
- Application metrics: Response times, error rates, throughput
- Infrastructure metrics: CPU, memory, disk, network
- Business metrics: Active users, messages/day, token usage
- Alerts: Error rate > 5%, latency > 3s, service down
