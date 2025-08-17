# WebSocket Scaling for Online Memory Game Platform

## Problem Statement

Design a scalable WebSocket infrastructure for an online memory game platform where:

- Players take turns flipping cards to find matching pairs
- System needs to handle **10 million concurrent users**
- Real-time communication is essential for game state synchronization
- Low latency requirements for competitive gameplay

## Table of Contents

1. [WebSocket Connection Capacity Analysis](#websocket-connection-capacity-analysis)
2. [Server Requirements Calculation](#server-requirements-calculation)
3. [State Management Strategies](#state-management-strategies)
4. [Scalable Architecture Patterns](#scalable-architecture-patterns)
5. [Load Balancing and Distribution](#load-balancing-and-distribution)
6. [Failover and High Availability](#failover-and-high-availability)
7. [Performance Monitoring](#performance-monitoring)
8. [Implementation Considerations](#implementation-considerations)

## WebSocket Connection Capacity Analysis

### Theoretical Limits per Server

#### Memory Constraints

Each WebSocket connection consumes:

- **TCP socket**: ~8KB (kernel buffers)
- **Application memory**: 2-4KB per connection (connection object, buffers)
- **Total per connection**: ~10-12KB

For a server with 32GB RAM:

```
Available for connections = 24GB (leaving 8GB for OS and application)
Max connections = 24GB / 12KB ≈ 2M connections
```

#### File Descriptor Limits

- Default Linux limit: 1024 file descriptors
- Optimized limit: 1M+ file descriptors
- Each WebSocket connection uses 1 file descriptor

#### CPU Considerations

- Modern server (16+ cores): Can handle 50K-100K concurrent connections
- Event-driven architectures (Node.js, Go) are more efficient
- CPU becomes bottleneck before memory for active connections

### Practical Connection Limits

#### Conservative Estimate

- **Per server capacity**: 50,000-100,000 concurrent connections
- **Reasoning**: Accounts for message processing, game logic, and safety margins

#### Optimized Setup

- **Per server capacity**: 200,000-500,000 concurrent connections
- **Reasoning**: Highly optimized servers with minimal per-connection overhead

## Server Requirements Calculation

### For 10M Concurrent Users

#### Conservative Approach

```
Target: 10,000,000 concurrent users
Per server capacity: 50,000 connections
Required servers: 10M / 50K = 200 servers
```

#### Optimized Approach

```
Target: 10,000,000 concurrent users
Per server capacity: 200,000 connections
Required servers: 10M / 200K = 50 servers
```

#### Recommended Production Setup

```
Base requirement: 50-200 servers
Safety factor (2x): 100-400 servers
Peak load buffer (1.5x): 150-600 servers

Final recommendation: 200-300 servers
```

### Server Specifications

```yaml
CPU: 16+ cores (Intel Xeon or AMD EPYC)
RAM: 64GB minimum (128GB preferred)
Network: 10Gbps minimum
Storage: NVMe SSD for logging and temporary data
```

## State Management Strategies

### Option 1: In-Memory State (WebServer-Based)

#### Advantages

```
✅ Ultra-low latency (microseconds)
✅ Simple implementation
✅ No network overhead for state access
✅ Strong consistency within server
```

#### Disadvantages

```
❌ State lost on server restart
❌ Difficult to scale horizontally
❌ No cross-server game support
❌ Complex failover handling
```

#### Implementation

```javascript
class GameServer {
  constructor() {
    this.activeGames = new Map(); // gameId -> GameState
    this.playerConnections = new Map(); // playerId -> WebSocket
  }

  handleGameMove(gameId, playerId, move) {
    const game = this.activeGames.get(gameId);
    game.processMove(playerId, move);
    this.broadcastToGame(gameId, game.getState());
  }
}
```

### Option 2: External Storage (Redis-Based)

#### Advantages

```
✅ Persistent state across server restarts
✅ Horizontal scaling support
✅ Cross-server game capabilities
✅ Simplified failover
✅ Centralized game state management
```

#### Disadvantages

```
❌ Network latency overhead (1-5ms)
❌ Additional infrastructure complexity
❌ Potential single point of failure
❌ Higher operational costs
```

#### Implementation

```javascript
class GameServer {
  constructor() {
    this.redis = new RedisClient();
    this.playerConnections = new Map();
  }

  async handleGameMove(gameId, playerId, move) {
    const gameState = await this.redis.get(`game:${gameId}`);
    const updatedState = this.processMove(gameState, playerId, move);
    await this.redis.set(`game:${gameId}`, updatedState);
    this.broadcastToGame(gameId, updatedState);
  }
}
```

### Hybrid Approach (Recommended)

#### Strategy

```
Local Cache: Recently accessed game states
Redis: Persistent storage and cross-server synchronization
Write-through: Updates go to both local cache and Redis
```

#### Benefits

```
✅ Low latency for active games
✅ Persistence and scalability
✅ Fault tolerance
✅ Optimal resource utilization
```

## Scalable Architecture Patterns

### Pattern 1: Horizontal Partitioning

#### Game-Based Sharding

```
Shard 1: Games 0-999,999
Shard 2: Games 1M-1.999M
...
Shard N: Games (N-1)M to NM-1
```

#### Player-Based Sharding

```
Shard determination: hash(playerId) % num_shards
Ensures: Players consistently connect to same shard
```

### Pattern 2: Geographic Distribution

#### Multi-Region Setup

```yaml
US-West: 30% of servers (3M users)
US-East: 25% of servers (2.5M users)
Europe: 25% of servers (2.5M users)
Asia: 20% of servers (2M users)
```

#### Benefits

- Reduced latency for global users
- Natural load distribution
- Disaster recovery capabilities

### Pattern 3: Microservices Architecture

#### Service Breakdown

```yaml
WebSocket Gateway: Handle connections only
Game Logic Service: Process game moves
Matchmaking Service: Pair players
State Management Service: Handle persistence
Notification Service: Push updates
```

## Load Balancing and Distribution

### WebSocket-Aware Load Balancing

#### Sticky Sessions

```nginx
upstream websocket_servers {
    ip_hash;  # Ensures same client goes to same server
    server ws1.game.com:8080;
    server ws2.game.com:8080;
    server ws3.game.com:8080;
}
```

#### Connection-Based Routing

```yaml
Strategy: Route based on current connection count
Algorithm: Least connections
Health Checks: Regular WebSocket ping/pong
```

### Auto-Scaling Triggers

#### Scale-Up Conditions

```yaml
CPU Usage: > 70% for 5 minutes
Memory Usage: > 80% for 3 minutes
Connection Count: > 80% of capacity
Response Time: > 100ms average
```

#### Scale-Down Conditions

```yaml
CPU Usage: < 30% for 15 minutes
Connection Count: < 40% of capacity
Grace Period: 30 minutes minimum
```

## Failover and High Availability

### Connection Recovery Strategies

#### Client-Side Reconnection

```javascript
class ResilientWebSocket {
  constructor(url) {
    this.url = url;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.connect();
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onclose = () => this.handleReconnect();
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect();
      }, Math.pow(2, this.reconnectAttempts) * 1000);
    }
  }
}
```

#### Server-Side State Recovery

```yaml
Game State Snapshots: Every 30 seconds to Redis
Connection Metadata: Player-to-server mapping
Recovery Process: 1. Detect server failure
  2. Redistribute connections
  3. Restore game states
  4. Notify clients to reconnect
```

### Health Monitoring

#### WebSocket Health Checks

```javascript
setInterval(() => {
  connections.forEach((ws) => {
    if (ws.isAlive === false) {
      ws.terminate();
      return;
    }
    ws.isAlive = false;
    ws.ping();
  });
}, 30000);
```

## Performance Monitoring

### Key Metrics

#### Connection Metrics

```yaml
Active Connections: Current WebSocket connections
Connection Rate: New connections per second
Disconnection Rate: Closed connections per second
Connection Duration: Average session length
```

#### Performance Metrics

```yaml
Message Latency: End-to-end message delivery time
Throughput: Messages processed per second
CPU Utilization: Per-server CPU usage
Memory Usage: RAM consumption per server
Network I/O: Bandwidth utilization
```

#### Game-Specific Metrics

```yaml
Games in Progress: Active memory game sessions
Average Game Duration: Time from start to completion
Player Actions per Game: Move frequency analysis
Concurrent Games per Server: Load distribution
```

### Monitoring Stack

```yaml
Metrics Collection: Prometheus
Visualization: Grafana
Alerting: AlertManager
Logging: ELK Stack (Elasticsearch, Logstash, Kibana)
Tracing: Jaeger for distributed tracing
```

## Implementation Considerations

### Technology Stack Recommendations

#### Backend Technologies

```yaml
Primary Choice: Node.js with Socket.io
Alternative: Go with Gorilla WebSocket
High Performance: C++ with uWebSockets
Managed Option: AWS API Gateway WebSocket
```

#### Infrastructure

```yaml
Container Orchestration: Kubernetes
Service Mesh: Istio for advanced routing
Message Queue: Apache Kafka for event streaming
Cache: Redis Cluster for distributed caching
Database: PostgreSQL for persistent data
```

### Security Considerations

#### WebSocket Security

```yaml
Authentication: JWT tokens in WebSocket headers
Rate Limiting: Per-connection message limits
DDoS Protection: Connection throttling by IP
Data Validation: Strict message format validation
```

### Cost Optimization

#### Resource Efficiency

```yaml
Connection Pooling: Reuse server resources
Compression: Enable WebSocket message compression
Graceful Degradation: Reduce features under high load
Auto-scaling: Dynamic server provisioning
```

#### Estimated Costs (AWS)

```yaml
200 c5.4xlarge instances: $50,000/month
Redis Cluster (50 nodes): $15,000/month
Load Balancers: $2,000/month
Monitoring & Logging: $3,000/month
Total Monthly Cost: ~$70,000
Cost per concurrent user: $0.007/month
```

## Handling Dropped WebSocket Connections

### Connection Drop Scenarios

#### Network-Level Drops

```yaml
Causes:
  - Temporary network interruption
  - Client device going offline
  - Network switching (WiFi to mobile data)
  - Router/ISP issues

Detection Time: 30-60 seconds (TCP keepalive)
Recovery: Client-side reconnection with exponential backoff
```

#### Application-Level Drops

```yaml
Causes:
  - Browser tab closure/navigation
  - Mobile app backgrounding
  - Client-side crashes
  - Deliberate disconnection

Detection Time: Immediate (close event)
Recovery: Depends on user intent
```

### Drop Detection Mechanisms

#### Server-Side Detection

```javascript
class ConnectionManager {
  constructor() {
    this.connections = new Map(); // playerId -> {ws, gameId, lastPing}
    this.startHeartbeat();
  }

  startHeartbeat() {
    setInterval(() => {
      this.connections.forEach((conn, playerId) => {
        if (Date.now() - conn.lastPing > 30000) {
          this.handleDroppedConnection(playerId, "timeout");
        } else {
          conn.ws.ping();
        }
      });
    }, 15000);
  }

  handleDroppedConnection(playerId, reason) {
    const conn = this.connections.get(playerId);
    if (conn) {
      this.notifyGameOfPlayerDrop(conn.gameId, playerId, reason);
      this.connections.delete(playerId);
    }
  }
}
```

#### Client-Side Detection

```javascript
class GameClient {
  constructor(url) {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.gameState = null;
    this.connect(url);
  }

  connect(url) {
    this.ws = new WebSocket(url);

    this.ws.onclose = (event) => {
      console.log(`Connection closed: ${event.code} - ${event.reason}`);
      if (event.code !== 1000) {
        // Not normal closure
        this.attemptReconnection();
      }
    };

    this.ws.onerror = () => {
      this.attemptReconnection();
    };
  }

  attemptReconnection() {
    if (this.reconnectAttempts < 5) {
      const delay = Math.pow(2, this.reconnectAttempts) * 1000;
      setTimeout(() => {
        this.reconnectAttempts++;
        this.connect(this.originalUrl);
      }, delay);
    }
  }
}
```

### Game State Recovery After Reconnection

#### Immediate Reconnection (< 30 seconds)

```javascript
// Server maintains temporary player session
class GameSessionManager {
  handleReconnection(playerId, newWebSocket) {
    const session = this.temporarySessions.get(playerId);
    if (session && Date.now() - session.disconnectTime < 30000) {
      // Restore player to active game
      this.connections.set(playerId, {
        ws: newWebSocket,
        gameId: session.gameId,
        lastPing: Date.now(),
      });

      // Send current game state to reconnected player
      this.sendGameState(playerId, session.gameId);

      // Notify other players of reconnection
      this.broadcastToGame(session.gameId, {
        type: "player_reconnected",
        playerId: playerId,
      });

      this.temporarySessions.delete(playerId);
      return true;
    }
    return false;
  }
}
```

#### Extended Disconnection (> 30 seconds)

```yaml
Strategy 1: Game Pause
  - Pause game for up to 2 minutes
  - Allow reconnection with full state restoration
  - Resume game when player returns

Strategy 2: AI Takeover
  - Replace disconnected player with AI
  - Continue game normally
  - Allow human player to rejoin and take over

Strategy 3: Game Abandonment
  - Mark game as incomplete
  - Award partial points to remaining players
  - Clean up game resources
```

## Server Restart Scenarios

### Graceful Restart with Zero Downtime

#### Pre-Restart Preparation

```javascript
class GracefulShutdown {
  async initiateShutdown() {
    console.log("Starting graceful shutdown...");

    // 1. Stop accepting new connections
    this.server.close();

    // 2. Notify load balancer to stop routing traffic
    await this.updateLoadBalancerHealth(false);

    // 3. Persist all active game states
    await this.persistAllGameStates();

    // 4. Notify clients of impending disconnection
    this.notifyClientsOfMaintenance();

    // 5. Wait for games to reach safe checkpoint
    await this.waitForSafeGameStates();

    // 6. Close all connections
    this.closeAllConnections();

    console.log("Graceful shutdown complete");
    process.exit(0);
  }

  async persistAllGameStates() {
    const activeGames = this.gameManager.getAllActiveGames();
    const promises = activeGames.map((game) =>
      this.redis.setex(`game:${game.id}`, 3600, JSON.stringify(game.state))
    );
    await Promise.all(promises);
  }

  notifyClientsOfMaintenance() {
    this.connections.forEach((conn) => {
      conn.ws.send(
        JSON.stringify({
          type: "server_maintenance",
          message: "Server restarting in 30 seconds. Please reconnect.",
          reconnectDelay: 30000,
        })
      );
    });
  }
}
```

#### Post-Restart Recovery

```javascript
class ServerRecovery {
  async restoreFromShutdown() {
    console.log("Starting server recovery...");

    // 1. Restore game states from Redis
    await this.restoreGameStates();

    // 2. Restore player-to-game mappings
    await this.restorePlayerMappings();

    // 3. Update load balancer health
    await this.updateLoadBalancerHealth(true);

    // 4. Handle reconnecting clients
    this.setupReconnectionHandling();

    console.log("Server recovery complete");
  }

  async restoreGameStates() {
    const gameKeys = await this.redis.keys("game:*");
    for (const key of gameKeys) {
      const gameState = await this.redis.get(key);
      if (gameState) {
        const game = JSON.parse(gameState);
        this.gameManager.restoreGame(game);
      }
    }
  }
}
```

### Emergency Restart (Crash Recovery)

#### Crash Detection and Failover

```yaml
Health Check Failure: 1. Load balancer detects unresponsive server
  2. Stops routing traffic to failed server
  3. Triggers auto-scaling to replace instance
  4. Game states recovered from Redis on new instance

Client Handling: 1. Clients detect connection loss
  2. Automatic reconnection to healthy servers
  3. Game state restoration from persistent storage
  4. Resume gameplay with minimal disruption
```

## External State Storage Deep Dive

### Connection Mapping Storage

#### Redis Data Structures for WebSocket Management

```javascript
// Structure 1: Game to Players Mapping
class GameConnectionManager {
  async addPlayerToGame(gameId, playerId, serverId) {
    // Store which server handles this player
    await this.redis.hset(`game:${gameId}:players`, playerId, serverId);

    // Store player's current game
    await this.redis.set(`player:${playerId}:game`, gameId);

    // Add to server's connection list
    await this.redis.sadd(`server:${serverId}:players`, playerId);
  }

  async getGamePlayers(gameId) {
    return await this.redis.hgetall(`game:${gameId}:players`);
  }

  async findPlayerServer(playerId) {
    const gameId = await this.redis.get(`player:${playerId}:game`);
    if (gameId) {
      return await this.redis.hget(`game:${gameId}:players`, playerId);
    }
    return null;
  }
}
```

#### Detailed Storage Schema

```redis
# Game State Storage
game:12345 = {
  "id": "12345",
  "players": ["player1", "player2"],
  "currentTurn": "player1",
  "board": [...],
  "status": "in_progress",
  "lastUpdate": 1640995200000
}

# Player to Game Mapping
player:player1:game = "12345"
player:player2:game = "12345"

# Game to Players with Server Assignment
game:12345:players = {
  "player1": "server-01",
  "player2": "server-02"
}

# Server Connection Lists
server:server-01:players = ["player1", "player3", "player5"]
server:server-02:players = ["player2", "player4", "player6"]

# Connection Metadata
connection:player1 = {
  "serverId": "server-01",
  "connectTime": 1640995200000,
  "lastSeen": 1640995800000,
  "gameId": "12345"
}
```

### Cross-Server Communication

#### Message Routing Between Servers

```javascript
class CrossServerMessaging {
  constructor() {
    this.redis = new RedisClient();
    this.serverId = process.env.SERVER_ID;
    this.setupSubscriptions();
  }

  setupSubscriptions() {
    // Subscribe to messages for this server
    this.redis.subscribe(`server:${this.serverId}:messages`);

    this.redis.on("message", (channel, message) => {
      const data = JSON.parse(message);
      this.handleCrossServerMessage(data);
    });
  }

  async sendToPlayer(playerId, message) {
    const serverMapping = await this.redis.hget(
      `game:${message.gameId}:players`,
      playerId
    );

    if (serverMapping === this.serverId) {
      // Player is on this server - send directly
      this.sendDirectly(playerId, message);
    } else {
      // Player is on different server - route through Redis
      await this.redis.publish(
        `server:${serverMapping}:messages`,
        JSON.stringify({
          type: "route_to_player",
          playerId: playerId,
          message: message,
        })
      );
    }
  }

  handleCrossServerMessage(data) {
    switch (data.type) {
      case "route_to_player":
        this.sendDirectly(data.playerId, data.message);
        break;
      case "game_update":
        this.updateLocalGameState(data.gameId, data.state);
        break;
    }
  }
}
```

### Data Consistency and Synchronization

#### Write-Through Cache Pattern

```javascript
class StateManager {
  async updateGameState(gameId, newState) {
    // 1. Update local cache
    this.localCache.set(gameId, newState);

    // 2. Update Redis (persistent storage)
    await this.redis.setex(`game:${gameId}`, 3600, JSON.stringify(newState));

    // 3. Notify other servers of update
    await this.redis.publish(
      "game_updates",
      JSON.stringify({
        gameId: gameId,
        state: newState,
        serverId: this.serverId,
        timestamp: Date.now(),
      })
    );
  }

  async getGameState(gameId) {
    // 1. Try local cache first
    let state = this.localCache.get(gameId);
    if (state) return state;

    // 2. Fallback to Redis
    const redisState = await this.redis.get(`game:${gameId}`);
    if (redisState) {
      state = JSON.parse(redisState);
      this.localCache.set(gameId, state); // Update local cache
      return state;
    }

    return null;
  }
}
```

## Internal vs External State Storage Comparison

### Internal State Storage (In-Memory)

#### Advantages

```yaml
Performance: ✅ Sub-millisecond access times
  ✅ No network latency
  ✅ Direct memory access
  ✅ CPU cache efficiency

Simplicity: ✅ Straightforward implementation
  ✅ No external dependencies
  ✅ Simplified debugging
  ✅ Reduced operational complexity
```

#### Disadvantages

```yaml
Scalability: ❌ Limited to single server capacity
  ❌ Difficult horizontal scaling
  ❌ No cross-server game support
  ❌ Memory constraints per server

Reliability: ❌ Data loss on server crashes
  ❌ No disaster recovery
  ❌ Complex failover procedures
  ❌ Game state not portable

Maintenance: ❌ Challenging rolling updates
  ❌ Downtime during restarts
  ❌ Difficult capacity planning
  ❌ No state backup/restore
```

### External State Storage (Redis-Based)

#### Advantages

```yaml
Scalability: ✅ Unlimited horizontal scaling
  ✅ Cross-server game support
  ✅ Independent scaling of storage
  ✅ Better resource utilization

Reliability: ✅ Persistent state storage
  ✅ Automatic failover support
  ✅ Built-in replication
  ✅ Point-in-time recovery

Operational: ✅ Zero-downtime deployments
  ✅ Easy server replacements
  ✅ Simplified monitoring
  ✅ Centralized state management
```

#### Disadvantages

```yaml
Performance: ❌ Network latency (1-5ms)
  ❌ Serialization overhead
  ❌ Additional CPU for Redis ops
  ❌ Potential throughput limits

Complexity: ❌ More moving parts
  ❌ Network partition handling
  ❌ Redis cluster management
  ❌ Consistency considerations

Cost: ❌ Additional infrastructure
  ❌ Redis licensing/hosting
  ❌ Higher operational overhead
  ❌ More skilled personnel needed
```

### Hybrid Approach Benefits

#### Best of Both Worlds

```yaml
Local Cache Layer:
  - Recent game states in memory
  - Sub-millisecond access for active games
  - Reduced Redis load
  - Better user experience

Redis Persistence Layer:
  - All game states persisted
  - Cross-server accessibility
  - Disaster recovery capability
  - Simplified scaling

Implementation Strategy:
  - Cache-aside pattern for reads
  - Write-through for updates
  - TTL-based cache eviction
  - Lazy loading for cache misses
```

#### Real-World Performance Comparison

```yaml
Internal Storage:
  - Read Latency: 0.01ms
  - Write Latency: 0.01ms
  - Throughput: 1M+ ops/sec
  - Scalability: Limited to server RAM

External Storage (Redis):
  - Read Latency: 1-3ms
  - Write Latency: 1-5ms
  - Throughput: 100K-500K ops/sec
  - Scalability: Virtually unlimited

Hybrid Approach:
  - Read Latency: 0.01ms (cache hit), 1-3ms (cache miss)
  - Write Latency: 1-5ms
  - Throughput: 500K+ ops/sec
  - Scalability: Unlimited with performance benefits
```

## Conclusion

For a 10M concurrent user memory game platform:

1. **Server Requirements**: 200-300 optimized servers
2. **Architecture**: Hybrid state management with Redis + local caching
3. **Connection Capacity**: 50K-200K connections per server
4. **Technology**: Node.js/Go with Redis Cluster
5. **Estimated Cost**: $70K/month on AWS

**Key Recommendations:**

- Use **external state storage** for scalability and reliability
- Implement **hybrid caching** for performance optimization
- Design **graceful failure handling** for dropped connections
- Plan **zero-downtime deployments** with proper state persistence
- Monitor **connection health** proactively with heartbeats

The key to success is implementing proper monitoring, auto-scaling, and failover mechanisms while maintaining low latency for real-time gameplay.
