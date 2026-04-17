# PLATO Technical White Paper
## The Engineer Guide to Building and Deploying Experience Infrastructure

**Version 1.0 — April 2026**

---

# PLATO Technical White Paper  
**Sections 1-3: Architecture, Data Model, and Core Algorithms**  
*Version 1.0*

---

## Section 1: Architecture Overview

PLATO (Patterned Learning and Adaptive Thought Organizer) is a real-time experiential learning system designed to capture, organize, and synthesize knowledge through structured question-answer interactions. The system operates on constrained edge hardware while maintaining responsive, multi-room conversational environments. Below is the architectural blueprint.

### 1.1 Hardware & Deployment Specifications
- **Hardware Platform**: NVIDIA Jetson Orin Nano 8GB
- **Memory Budget**: 15MB RAM (application footprint target)
- **Network Protocol**: WebSocket (26 concurrent rooms)
- **Persistence**: JSON flat-file system
- **Management**: systemd service with auto-recovery
- **Debug Interface**: Telnet on port 4040

### 1.2 Architectural Text Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATO Core System                         │
├─────────────┬──────────────────────────────┬─────────────────┤
│   Layer 1   │         Layer 2              │    Layer 3      │
│  Interface  │        Processing            │   Persistence   │
├─────────────┼──────────────────────────────┼─────────────────┤
│             │                              │                 │
│ • WebSocket │ • Gear 1: Pattern Matcher    │ • Tile Store    │
│   (26 rooms)│   - Cosine similarity        │   (JSON files)  │
│             │   - Score-weighted top-k     │                 │
│ • Telnet    │                              │ • Room Config   │
│   (:4040)   │ • Gear 2: LLM Synthesizer    │   (YAML files)  │
│             │   - Provider abstraction     │                 │
│ • Systemd   │   - Token/temp controls      │ • Session Logs  │
│   service   │                              │   (JSONL)       │
│             │ • Clunk Detector             │                 │
│             │   - Iteration gap analysis   │                 │
├─────────────┼──────────────────────────────┼─────────────────┤
│             │         Data Flow            │                 │
│  Request →  │  Room → Gear 1 → Gear 2 →    │  → Tile Update  │
│  Response   │        (Fallback logic)      │   → Persistence │
└─────────────┴──────────────────────────────┴─────────────────┘
```

### 1.3 Two-Gear NPC System
PLATO implements a dual-processing engine called the "Two-Gear NPC":

**Gear 1: Pattern Matcher**
- Real-time similarity search across existing tiles
- Uses sentence embeddings (all-MiniLM-L6-v2, 22MB)
- Operates entirely within RAM constraints
- Returns top-k matches with confidence scores

**Gear 2: LLM Synthesizer**
- Activated when Gear 1 confidence < threshold (default: 0.85)
- Abstracts multiple LLM providers (OpenAI, Anthropic, Local)
- Applies room-specific parameters (temperature, max_tokens)
- Generates novel responses while creating new tiles

### 1.4 Concurrency Model
```
26 Independent Rooms → 26 WebSocket Connections
    ↓
Room Manager (Async/Non-blocking I/O)
    ↓
Worker Pool (4 threads) → Tile Cache (LRU, 15MB cap)
    ↓
File I/O Scheduler (Sequential writes, batch updates)
```

### 1.5 System Characteristics
- **Stateless Design**: Each room independent, shared tile repository
- **Fail-Fast**: Unresponsive Gear 2 falls back to Gear 1 patterns
- **Progressive Enhancement**: New tiles improve future matching
- **Observability**: Telnet interface for real-time debugging

---

## Section 2: Data Model

PLATO's data model centers on three core entities: Tiles (knowledge units), Rooms (conversation contexts), and Sessions (interaction logs).

### 2.1 Tile Schema
Tiles represent atomic Q&A pairs with metadata for learning optimization.

```json
{
  "id": "tile_abc123def456",
  "instruction": "How does photosynthesis work?",
  "input": "Explain the process in simple terms",
  "output": "Photosynthesis converts sunlight into chemical energy...",
  "score": 0.92,
  "metadata": {
    "room": "biology_lab",
    "tags": ["science", "plants", "energy"],
    "complexity": 0.7,
    "response_time_ms": 245
  },
  "provenance": {
    "source": "llm_synthesis",
    "model": "gpt-4",
    "parent_tiles": ["tile_xyz789", "tile_abc456"],
    "confidence": 0.88
  },
  "created": "2024-01-15T10:30:00Z",
  "updated": "2024-01-15T10:30:00Z",
  "access_count": 17,
  "feedback_history": [
    {"timestamp": "2024-01-15T10:35:00Z", "delta": +0.1},
    {"timestamp": "2024-01-16T14:20:00Z", "delta": -0.05}
  ]
}
```

**Field Specifications**:
- `id`: UUID v4 with "tile_" prefix
- `instruction`: The core question or task (max 200 chars)
- `input`: Specific phrasing or context (max 500 chars)
- `output`: Response content (max 2000 chars)
- `score`: 0.0-1.0 quality metric, adjusted via feedback
- `metadata`: Room context and performance data
- `provenance`: Lineage tracking for knowledge graph
- `created/updated`: ISO 8601 timestamps
- `access_count`: Usage frequency for cache optimization
- `feedback_history`: Score adjustment audit trail

### 2.2 Room Schema (YAML)
Rooms define isolated conversation environments with LLM parameters.

```yaml
name: "physics_classroom"
description: "Undergraduate physics Q&A with step-by-step explanations"
system_prompt: |
  You are a patient physics tutor. Break down complex concepts into
  fundamental principles. Use analogies when helpful. Always acknowledge
  when you're uncertain.

tile_dir: "/var/plato/tiles/physics"
max_tokens: 1000
temperature: 0.3
llm_provider:
  name: "openai"
  model: "gpt-4-turbo-preview"
  api_key_env: "OPENAI_KEY"
  timeout_seconds: 30

gear1_threshold: 0.85
top_k_matches: 5
embedding_model: "all-MiniLM-L6-v2"

retention_policy:
  max_tiles: 10000
  cleanup_days: 90
  archive_on_full: true

clunk_detection:
  max_iterations: 4
  gap_threshold: 0.4
  auto_purge: false
```

**Critical Parameters**:
- `tile_dir`: Isolated tile storage per room
- `temperature`: Lower (0.1-0.4) for technical rooms, higher for creative
- `gear1_threshold`: Similarity cutoff for Gear 2 activation
- `clunk_detection`: Prevents conversational dead-ends

### 2.3 Session Schema
Sessions log complete interactions for analysis and training.

```json
{
  "session_id": "sess_20240115_1030_abc123",
  "room": "physics_classroom",
  "start_time": "2024-01-15T10:30:00Z",
  "end_time": "2024-01-15T11:15:00Z",
  "user_id": "user_789",
  "interactions": [
    {
      "sequence": 1,
      "timestamp": "2024-01-15T10:30:15Z",
      "user_input": "What is quantum entanglement?",
      "system_response": "Quantum entanglement is when particles...",
      "tiles_used": ["tile_phys001", "tile_phys045"],
      "gear_used": 2,
      "response_time_ms": 1203,
      "confidence_score": 0.91
    },
    {
      "sequence": 2,
      "timestamp": "2024-01-15T10:32:45Z",
      "user_input": "Can you give a real-world example?",
      "system_response": "In quantum cryptography...",
      "tiles_used": ["tile_phys045", "tile_phys102"],
      "gear_used": 1,
      "response_time_ms": 45,
      "confidence_score": 0.96
    }
  ],
  "summary": {
    "total_interactions": 12,
    "gear1_count": 8,
    "gear2_count": 4,
    "avg_confidence": 0.89,
    "new_tiles_generated": 2,
    "clunks_detected": 0
  }
}
```

### 2.4 Data Relationships
```
Room (1) → (n) Tiles
Room (1) → (n) Sessions
Tile (n) → (n) Tiles (via provenance.parent_tiles)
Session (1) → (n) Interactions → (n) Tiles
```

### 2.5 Storage Optimization
Given 15MB RAM constraint:
- **Tile Cache**: LRU with 1000-tile limit (~5MB)
- **Embeddings**: 384-dim floats, 1.5KB/tile compressed
- **Session Logs**: JSONL rotation, 100 sessions/file
- **Index Files**: Bloom filters for rapid tile lookup

---

## Section 3: Core Algorithms

### 3.1 Tile Matching Algorithm
The pattern matching engine (Gear 1) uses semantic similarity to find relevant tiles.

```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import heapq

class TileMatcher:
    def __init__(self, embedding_model='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(embedding_model)
        self.tile_embeddings = {}  # tile_id -> embedding
        self.tile_scores = {}      # tile_id -> score
        
    def find_top_k(self, query, k=5, threshold=0.7):
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Calculate weighted similarities
        candidates = []
        for tile_id, tile_embedding in self.tile_embeddings.items():
            similarity = cosine_similarity(
                [query_embedding], 
                [tile_embedding]
            )[0][0]
            
            # Score-weighted similarity
            tile_score = self.tile_scores.get(tile_id, 0.5)
            weighted_sim = similarity * (0.3 + 0.7 * tile_score)
            
            if weighted_sim >= threshold:
                heapq.heappush(candidates, (weighted_sim, tile_id))
                
        # Return top-k
        top_k = heapq.nlargest(k, candidates)
        return [
            {
                'tile_id': tile_id,
                'similarity': sim,
                'weighted_similarity': sim
            }
            for sim, tile_id in top_k
        ]
    
    def update_embeddings(self, tiles_batch):
        """Batch update embeddings for new/updated tiles"""
        texts = [f"{t['instruction']} {t['input']}" for t in tiles_batch]
        embeddings = self.model.encode(texts)
        
        for tile, embedding in zip(tiles_batch, embeddings):
            self.tile_embeddings[tile['id']] = embedding
            self.tile_scores[tile['id']] = tile['score']
```

**Algorithm Complexity**:
- Embedding generation: O(n) where n = tile count
- Similarity search: O(n) linear scan (optimized with caching)
- Memory: O(n × d) where d = 384 dimensions

### 3.2 Clunk Detection Algorithm
Identifies conversational dead-ends through iteration analysis.

```python
class ClunkDetector:
    def __init__(self, max_iterations=4, gap_threshold=0.4):
        self.max_iterations = max_iterations
        self.gap_threshold = gap_threshold
        self.conversation_state = {}  # room_id -> state
        
    def analyze_interaction(self, room_id, user_input, 
                           response_confidence, response_time_ms):
        if room_id not in self.conversation_state:
            self.conversation_state[room_id] = {
                'iterations': 0,
                'confidence_history': [],
                'topic_coherence': 1.0
            }
        
        state = self.conversation_state[room_id]
        state['iterations'] += 1
        state['confidence_history'].append(response_confidence)
        
        # Detect confidence gap
        if len(state['confidence_history']) >= 2:
            recent_avg = np.mean(state['confidence_history'][-2:])
            earlier_avg = np.mean(state['confidence_history'][-4:-2]) \
                         if len(state['confidence_history']) >= 4 else 1.0
            
            confidence_gap = earlier_avg - recent_avg
            
            # Clunk detection logic
            if (state['iterations'] >= self.max_iterations and 
                confidence_gap > self.gap_threshold):
                return {
                    'is_clunk': True,
                    'iterations': state['iterations'],
                    'confidence_gap': confidence_gap,
                    'suggestion': 'topic_shift'
                }
        
        return {'is_clunk': False}
    
    def reset_room(self, room_id):
        """Reset after successful resolution or topic shift"""
        if room_id in self.conversation_state:
            del self.conversation_state[room_id]
```

### 3.3 Tile Scoring Algorithm
Dynamic scoring based on feedback and usage patterns.

```python
class TileScorer:
    def __init__(self, 
                 initial_score=0.5,
                 feedback_weight=0.3,
                 usage_weight=0.2,
                 recency_weight=0.1):
        self.weights = {
            'feedback': feedback_weight,
            'usage': usage_weight,
            'recency': recency_weight,
            'provenance': 0.4
        }
    
    def calculate_score(self, tile, feedback_delta=0):
        """Calculate composite score for a tile"""
        
        # Base components
        feedback_component = self._feedback_component(
            tile['score'], 
            feedback_delta,
            tile.get('feedback_history', [])
        )
        
        usage_component = self._usage_component(
            tile.get('access_count', 0),
            tile.get('response_time_ms', 1000)
        )
        
        recency_component = self._recency_component(
            tile['updated']
        )
        
        provenance_component = self._provenance_component(
            tile.get('provenance', {})
        )
        
        # Weighted sum
        components = {
            'feedback': feedback_component,
            'usage': usage_component,
            'recency': recency_component,
            'provenance': provenance_component
        }
        
        total_weight = sum(self.weights.values())
        weighted_sum = sum(
            components[key] * self.weights[key]
            for key in self.weights
        )
        
        new_score = weighted_sum / total_weight
        
        # Clamp to [0, 1]
        return max(0.0, min(1.0, new_score))
    
    def _feedback_component(self, current_score, delta, history):
        """Calculate feedback-based score adjustment"""
        if not history:
            return current_score
        
        # Exponential decay of historical feedback
        decayed_sum = 0
        total_weight = 0
        for i, feedback in enumerate(reversed(history)):
            weight = np.exp(-i * 0.5)  # Half-life of ~1.4 entries
            decayed_sum += feedback['delta'] * weight
            total_weight += weight
        
        avg_feedback = decayed_sum / total_weight if total_weight > 0 else 0
        return current_score + (avg_feedback * 0.5) + (delta * 0.5)
    
    def _usage_component(self, access_count, response_time_ms):
        """Score based on usage patterns"""
        # Normalize access count (log scale)
        norm_access = np.log1p(access_count) / np.log1p(1000)
        
        # Response time penalty (faster = better)
        time_penalty = max(0, 1 - (response_time_ms / 5000))
        
        return (norm_access * 0.7) + (time_penalty * 0.3)
    
    def _recency_component(self, updated_timestamp):
        """Recency decay function"""
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        updated = datetime.fromisoformat(updated_timestamp.replace('Z', '+00:00'))
        
        days_old = (now - updated).days
        decay = np.exp(-days_old / 30)  # 30-day half-life
        
        return decay
    
    def _provenance_component(self, provenance):
        """Score based on tile lineage"""
        source_score = {
            'llm_synthesis': 0.8,
            'pattern_match': 0.9,
            'human_curated': 1.0,
            'imported': 0.7
        }.get(provenance.get('source', 'llm_synthesis'), 0.5)
        
        parent_count = len(provenance.get('parent_tiles', []))
        connectivity = min(1.0, parent_count / 10)  # Cap at 10 parents
        
        return (source_score * 0.6) + (connectivity

---


# PLATO Technical White Paper (Sections 4-7)

## 4. API Reference

### 4.1 WebSocket Message Protocol

PLATO’s primary real‑time interface is a JSON‑based WebSocket protocol operating on `/ws`. All messages share a common envelope structure:

```json
{
  "type": "message_type",
  "room": "room_name",
  "session_id": "uuid_v4_string",
  "timestamp": "2024-01-15T10:30:00Z",
  "message": { ... }
}
```

**Required Fields:**
- `type`: Determines message handling. Valid values: `join`, `leave`, `tile_update`, `query`, `response`, `error`.
- `room`: Target room identifier (must match existing room configuration).
- `session_id`: Unique client session identifier (generated on first connection).
- `message`: Payload object, structure varies by `type`.

#### 4.1.1 Client-to-Server Messages

**Join Room:**
```json
{
  "type": "join",
  "room": "cognitive_architecture",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": {
    "user_agent": "PLATO-CLI/1.0",
    "capabilities": ["tile_edit", "query"]
  }
}
```

**Submit Query:**
```json
{
  "type": "query",
  "room": "epistemology",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": {
    "query": "How do boundary tiles affect concept formation?",
    "context_tiles": ["tile_123", "tile_456"],
    "response_mode": "synthetic"
  }
}
```

**Update Tile:**
```json
{
  "type": "tile_update",
  "room": "design_patterns",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": {
    "tile_id": "tile_789",
    "content": {
      "title": "New Pattern Discovered",
      "body": "When boundary tiles form closed loops...",
      "score": 42,
      "type": "analogy"
    },
    "signature": "base64_hmac_sha256"
  }
}
```

#### 4.1.2 Server-to-Client Messages

**Tile Broadcast:**
```json
{
  "type": "tile_update",
  "room": "design_patterns",
  "session_id": "system",
  "timestamp": "2024-01-15T10:30:05Z",
  "message": {
    "tile_id": "tile_789",
    "content": {
      "title": "New Pattern Discovered",
      "body": "When boundary tiles form closed loops...",
      "score": 45,
      "type": "analogy",
      "author": "anonymous",
      "created": "2024-01-15T10:30:00Z"
    }
  }
}
```

**Query Response:**
```json
{
  "type": "response",
  "room": "epistemology",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": {
    "query_id": "qry_987654",
    "answer": "Boundary tiles create semantic edges that...",
    "supporting_tiles": ["tile_123", "tile_456", "tile_789"],
    "confidence": 0.87,
    "synthesized": true
  }
}
```

**Error Response:**
```json
{
  "type": "error",
  "room": "cognitive_architecture",
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": {
    "code": "ROOM_FULL",
    "message": "Room capacity (50 concurrent sessions) exceeded",
    "retry_after": 30
  }
}
```

### 4.2 REST Endpoints

PLATO provides HTTP REST API on port 8080 (configurable). All responses include standard headers:
```
X-PLATO-Version: 0.9.0
X-Room-Shard: shard_03
Content-Type: application/json
```

#### GET /api/info
Returns system metadata and health status.

**Example Request:**
```bash
curl -X GET http://localhost:8080/api/info
```

**Example Response:**
```json
{
  "system": "PLATO",
  "version": "0.9.0",
  "uptime_seconds": 86400,
  "rooms_active": 12,
  "sessions_active": 142,
  "tiles_total": 12500,
  "memory_usage_mb": 14.2,
  "llm_provider": "deepseek",
  "status": "healthy",
  "git_commit": "a1b2c3d4e5"
}
```

#### GET /api/rooms
Lists available rooms with metadata.

**Example Request:**
```bash
curl -X GET "http://localhost:8080/api/rooms?include_stats=true"
```

**Example Response:**
```json
{
  "rooms": [
    {
      "name": "cognitive_architecture",
      "title": "Cognitive Architecture Research",
      "description": "Models of mind and intelligence",
      "tile_count": 1250,
      "session_count": 18,
      "created": "2024-01-01T00:00:00Z",
      "last_activity": "2024-01-15T10:25:00Z",
      "read_only": false
    },
    {
      "name": "epistemology",
      "title": "Epistemological Foundations",
      "description": "Theories of knowledge and belief",
      "tile_count": 890,
      "session_count": 12,
      "created": "2024-01-02T00:00:00Z",
      "last_activity": "2024-01-15T09:45:00Z",
      "read_only": false
    }
  ],
  "total": 12,
  "limit": 50
}
```

#### GET /api/rooms/{name}/tiles
Retrieves tiles from specified room with pagination.

**Example Request:**
```bash
curl -X GET "http://localhost:8080/api/rooms/cognitive_architecture/tiles?limit=5&offset=0&sort_by=score"
```

**Example Response:**
```json
{
  "room": "cognitive_architecture",
  "tiles": [
    {
      "id": "tile_001",
      "type": "boundary",
      "title": "The Symbol Grounding Problem",
      "body": "Symbols must be grounded in sensorimotor experience...",
      "score": 156,
      "author": "anonymous",
      "created": "2024-01-01T12:00:00Z",
      "updated": "2024-01-15T09:30:00Z",
      "tags": ["symbols", "grounding", "embodiment"]
    },
    {
      "id": "tile_002",
      "type": "analogy",
      "title": "Neural Networks as Fluid Dynamics",
      "body": "Training dynamics resemble gradient flows...",
      "score": 142,
      "author": "anonymous",
      "created": "2024-01-02T14:30:00Z",
      "updated": "2024-01-14T16:45:00Z",
      "tags": ["analogy", "dynamics", "visualization"]
    }
  ],
  "pagination": {
    "total": 1250,
    "limit": 5,
    "offset": 0,
    "has_more": true
  }
}
```

#### POST /api/feedback
Submits system feedback or bug reports.

**Example Request:**
```bash
curl -X POST http://localhost:8080/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "category": "bug",
    "severity": "medium",
    "room": "cognitive_architecture",
    "message": "Tile scores occasionally reset during high load",
    "contact": "optional@email.com"
  }'
```

**Example Response:**
```json
{
  "status": "received",
  "feedback_id": "fb_123456",
  "message": "Feedback logged for review"
}
```

### 4.3 Telnet Interface

PLATO provides a legacy‑compatible Telnet interface on port 4040, supporting ANSI color and basic navigation.

**Connection Example:**
```bash
telnet localhost 4040
```

**Session Flow:**
```
PLATO Telnet Interface v0.9.0
Available rooms:
1) cognitive_architecture (18 users)
2) epistemology (12 users)
3) design_patterns (8 users)

Enter room number or name: cognitive_architecture

=== cognitive_architecture ===
Recent tiles:
[156] The Symbol Grounding Problem (boundary)
[142] Neural Networks as Fluid Dynamics (analogy)
[128] Emergent Symbols from Compression (meta)

Commands: /list, /view <id>, /query <text>, /exit

> /view tile_001

TILE: The Symbol Grounding Problem
TYPE: boundary
SCORE: 156
AUTHOR: anonymous
CREATED: 2024-01-01 12:00:00 UTC

Symbols must be grounded in sensorimotor experience
to avoid infinite regress of symbolic interpretation.
Harnad's 1990 formulation suggests...

> /query How does this relate to LLMs?

PROCESSING... (using DeepSeek)

RESPONSE: LLMs exhibit a form of statistical grounding
where symbols connect through distributional semantics
rather than physical experience. This creates...

SUPPORTING TILES: tile_001, tile_045, tile_128
```

**Telnet Protocol Details:**
- Plain text over TCP port 4040
- Line‑based input (max 1024 bytes per line)
- ANSI escape codes for formatting (optional)
- Auto‑disconnect after 1 hour of inactivity
- Maximum 10 concurrent Telnet sessions per instance

## 5. Deployment

### 5.1 System Requirements

**Minimum Hardware:**
- NVIDIA Jetson Orin Nano 8GB (or equivalent ARM64 with GPU)
- 4GB free storage
- 100Mbps network connection

**Recommended Production:**
- Multiple Jetson Orin Nano nodes (horizontal scaling)
- Load balancer (nginx, haproxy)
- CDN for static assets (jsDelivr, Cloudflare)

### 5.2 systemd User Service Configuration

PLATO runs as a user‑level systemd service on Jetson Orin Nano:

**Service File:** `~/.config/systemd/user/plato.service`
```ini
[Unit]
Description=PLATO Cognitive Environment
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec=10
User=%u
WorkingDirectory=/home/%u/plato
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
Environment="PLATO_ENV=production"
Environment="PLATO_PORT=8080"
Environment="PLATO_WS_PORT=8080"
Environment="PLATO_TELNET_PORT=4040"
Environment="PLATO_DATA_DIR=/home/%u/plato_data"
Environment="PLATO_MAX_MEMORY_MB=15"
Environment="PLATO_LLM_PROVIDER=deepseek"
Environment="DEEPSEEK_API_KEY=your_key_here"
Environment="GROQ_API_KEY=optional_key"
Environment="ANTHROPIC_API_KEY=optional_key"

# Resource constraints
MemoryMax=15M
CPUQuota=30%
IOWeight=100

ExecStart=/usr/bin/python3 -m plato.main --config /home/%u/plato/config.yaml
ExecStop=/bin/kill -TERM $MAINPID
ExecReload=/bin/kill -HUP $MAINPID

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/home/%u/plato_data

[Install]
WantedBy=default.target
```

**Installation Commands:**
```bash
# Copy service file
mkdir -p ~/.config/systemd/user
cp plato.service ~/.config/systemd/user/

# Enable lingering for user services
sudo loginctl enable-linger $USER

# Reload and start
systemctl --user daemon-reload
systemctl --user enable plato
systemctl --user start plato

# Check status
systemctl --user status plato
journalctl --user -u plato -f
```

### 5.3 Resource Constraints

PLATO operates under strict resource limits:

**Memory Management (15MB Total):**
- Tile cache: 8MB LRU (Least Recently Used)
- Session state: 4MB (WebSocket connections)
- LLM context buffer: 2MB
- System overhead: 1MB

**Configuration Example:** `config.yaml`
```yaml
resource_limits:
  memory_mb: 15
  max_sessions_per_room: 50
  max_tiles_per_room: 5000
  tile_cache_size: 1000
  session_timeout_seconds: 3600

performance:
  tile_compression: true  # gzip for storage
  batch_updates: true     # aggregate tile updates
  lazy_loading: true      # load tiles on demand

monitoring:
  metrics_port: 9090      # Prometheus metrics
  health_check_interval: 30
  log_level: "INFO"
```

### 5.4 Horizontal Scaling Architecture

**Room Sharding Strategy:**
```yaml
# shard_config.yaml
shards:
  - id: "shard_01"
    host: "plato-node-01.local"
    port: 8080
    rooms:
      - "cognitive_architecture"
      - "epistemology"
      - "philosophy_of_mind"
    capacity: 150  # max concurrent sessions
  
  - id: "shard_02"
    host: "plato-node-02.local"
    port: 8080
    rooms:
      - "design_patterns"
      - "software_architecture"
      - "systems_thinking"
    capacity: 150

load_balancer:
  strategy: "room_affinity"  # sticky sessions per room
  health_check: "/api/info"
  failover_timeout: 10
```

**CDN Configuration for Static Assets:**
```nginx
# nginx configuration
server {
    listen 80;
    server_name plato.example.com;
    
    location /ws {
        proxy_pass http://plato-backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
    
    location /api {
        proxy_pass http://plato-backend;
        proxy_set_header Host $host;
    }
    
    location /static/ {
        # CDN fallback configuration
        proxy_cache plato_cache;
        proxy_cache_valid 200 1h;
        add_header X-Cache-Status $upstream_cache_status;
        
        # Primary: CDN origin
        proxy_pass https://cdn.example.com/plato-static/;
        
        # Fallback: local assets
        error_page 502 503 504 = @static_fallback;
    }
    
    location @static_fallback {
        root /var/www/plato/static;
        expires 1h;
    }
}
```

### 5.5 Environment Variables

**Required:**
```bash
PLATO_ENV=production
PLATO_DATA_DIR=/path/to/data
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx
```

**Optional:**
```bash
# Multi-provider LLM configuration
GROQ_API_KEY=your_groq_key
SILICONFLOW_API_KEY=your_sf_key
ANTHROPIC_API_KEY=your_claude_key

# Performance tuning
PLATO_MAX_MEMORY_MB=15
PLATO_WORKER_THREADS=2
PLATO_IO_THREADS=1

# Network
PLATO_HOST=0.0.0.0
PLATO_PORT=8080
PLATO_TELNET_PORT=4040

# Security
PLATO_CORS_ORIGINS=https://app.example.com
PLATO_RATE_LIMIT=100/60  # 100 requests per minute
```

## 6. Extensibility

### 6.1 Creating Rooms

Rooms are defined through YAML configuration and tile JSON files:

**Room Definition:** `rooms/cognitive_architecture.yaml`
```yaml
room:
  name: "cognitive_architecture"
  title: "Cognitive Architecture Research"
  description: |
    Exploration of mind models, symbol grounding,
    and architectural patterns for intelligence.
  
  settings:
    public: true
    read_only: false
    allow_anonymous: true
    max_tiles: 5000
    tile_score_decay: 0.95  # per month
    moderation_level: "collaborative"
  
  initial_tiles:
    - file: "tiles/foundational.json"
      priority: 1
    - file: "tiles/embodiment.json"
      priority: 2
  
  llm_config:
    default_provider: "deepseek"
    temperature: 0.7
    max_tokens: 1000
    context_window: 8  # tiles to include
  
  plugins:
    - "tile_validator"
    - "analogy_detector"
    - "consensus_checker"
```

**Initial Tile File:** `tiles/foundational.json`
```json
[
  {
    "id": "tile_001",
    "type": "bound

---
*PLATO Technical White Paper — written by DeepSeek-chat, assembled by JC1*

