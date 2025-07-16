# Netflix's Active-Active Multi-Regional Resiliency

**Source**: [Netflix Tech Blog - Active-Active for Multi-Regional Resiliency](https://netflixtechblog.com/active-active-for-multi-regional-resiliency-c47719f6685b)

## Overview

This analysis covers how Netflix achieves multi-regional resiliency using Active-Active architecture to maintain 99.99% availability (only 52 minutes of downtime per year) across their global streaming platform.

## Foundational Concepts

### 1. Failure as a Function of Scale and Velocity

Netflix establishes a fundamental principle: **failure rates = f(scale, velocity)**

- **Scale**: As operational deployment grows, hardware failure chances increase
- **Velocity**: Fast pace of change increases software failure probability
- **Combined effect**: At large scale with high velocity, things break constantly

The types of failures Netflix focuses on are complete and prolonged service outages that result in:

- Unhappy customers flooding support lines
- Social media complaints
- Public articles announcing service downtime

### 2. Active-Active Architecture Principles

Netflix implements two core resilience principles:

- **Isolation**: Failure in one region doesn't affect another region
- **Redundancy**: Multiple regions provide backup capabilities

**Key Requirements for Active-Active:**

- **Stateless services**: All state management handled at data tier
- **Local resource access**: Services only access resources within their region (S3, SQS, etc.)
- **No cross-regional calls**: All data replication must be asynchronous

### 3. Geographic Traffic Distribution

**Normal operations**: 50/50 traffic split between:

- US-East-1 (Virginia)
- US-West-2 (Oregon)

**Failover mode**: All traffic directed to healthy region via geo-DNS override

## Netflix's Implementation Strategy

### 1. DNS-Based Traffic Control (Denominator)

Netflix uses a **dual-layer DNS approach**:

```
Users → UltraDNS → Route53 → ELBs
```

**Components:**

- **UltraDNS**: Provides directional routing based on geographic location
- **Route53**: Enables fast, reliable traffic switching between regions
- **Denominator**: Single client library controlling multiple DNS providers

**Why dual-layer?**

- UltraDNS handles geographic routing (not available in Route53)
- Route53 provides reliable API for fast configuration changes
- Simplified traffic switching by moving Route53 CNAMEs

**Example**: A user in California gets routed to US-West-2, while a user in New York gets routed to US-East-1.

### 2. Traffic Shaping with Zuul

**Zuul** (Netflix's edge service) provides enhanced capabilities for Active-Active:

**Mis-routed request handling**:

- Detects when users hit wrong region
- Can redirect to correct region or handle locally in "failover mode"
- Ensures single user session doesn't span multiple regions

**Traffic throttling**:

- Sets maximum traffic levels per region
- Automatically sheds excess load to protect downstream services
- Critical during failover when one region must handle 100% traffic

**Failover mode declaration**:

- Region stops routing mis-routed requests to other regions
- Handles all requests locally during emergency

**Example**: During failover, if US-East fails, Zuul gradually ramps up traffic to US-West while protecting services from being overwhelmed by thundering herd effects.

### 3. Data Replication Strategy

#### Apache Cassandra for Persistent Data

Netflix leverages Cassandra's **multi-datacenter asynchronous replication**:

**Normal operations:**

- **Write**: Data written to local region with CL_LOCAL_QUORUM
- **Replication**: Asynchronously replicates to other regions
- **Read**: Typically from local region with CL_ONE

**Active-Active changes:**

- Requests can come from either region
- Replication must happen within acceptable time threshold

**Consistency validation**: Netflix wrote 1 million records in one region, then successfully read them from another region 500ms later under production load.

#### EvCache for Cached Data

For Memcached consistency across regions, Netflix added **remote cache invalidation**:

```
Region A: Write → Cache Update → SQS Message → Region B: Cache Invalidation
```

**Process flow:**

1. Application writes data in Region A
2. Local cache updated in Region A
3. SQS message sent to Region B
4. Region B cache invalidated
5. Next read in Region B fetches fresh data from Cassandra

**Example**: User updates their profile in US-East:

1. Profile updated in Cassandra (US-East)
2. Cache updated in US-East
3. SQS message sent to US-West
4. US-West cache invalidated
5. Next read in US-West fetches fresh data from Cassandra

### 4. Multi-Regional Deployment (Mimir)

Netflix automated deployment across **6 environments**:

- **Test**: US-East, US-West, EU-West
- **Production**: US-East, US-West, EU-West

**Mimir workflow** (built on Glisten workflow language):

1. Deploy to Test environment
2. Run automated canary analysis
3. Deploy to Production with staged rollout
4. Wait hours between regional deployments
5. Automatic rollback if issues detected

**Benefits:**

- Developers don't need manual deployment to 6+ environments
- Staged deployment catches issues before worldwide rollout
- Automated canary analysis and rollback procedures

### 5. Chaos Engineering Validation

Netflix tests resilience with increasingly severe simulations:

**Chaos Monkey**: Kills individual instances (includes Cassandra clusters)
**Chaos Gorilla**: Takes out entire Availability Zones
**Split-brain**: Severs connectivity between regions
**Chaos Kong**: Simulates complete regional failure

#### Chaos Kong Exercise Details

**Objective**: Prove system can handle 100% load in single region

**Process:**

1. Gradually shift majority traffic from US-East to US-West
2. Maintain service for 24+ hours on single region
3. Gradually return to 50/50 stable state

**Modifications for user experience:**

- Users routed to "failed" region get redirected to healthy region
- Gradual traffic shifting (vs emergency rapid switching)
- Allow services to scale up and caches to warm up

**Results**: Successfully demonstrated ability to handle full Netflix US load in US-West-2

## Real-World Example: Actual Failover

Netflix experienced a real middle-tier system failure:

**Problem**: Severe degradation in US-East region

- Middle-tier system became unresponsive
- Majority of cluster affected
- Would normally result in severe user-impacting outage

**Response Timeline**:

1. **Detection**: Monitoring identified cluster becoming unresponsive
2. **Decision**: Execute regional failover instead of waiting for fix
3. **Action**: Route all traffic to healthy US-West region
4. **Result**: Service quality restored quickly for all users
5. **Recovery**: Root cause analysis, fix deployment, gradual traffic return

**Impact comparison:**

- **Without Active-Active**: Severe outage affecting many users for extended time
- **With Active-Active**: Seamless failover with minimal user impact

## Technical Challenges Solved

### 1. Effective Traffic Direction

- **Solution**: Denominator with UltraDNS + Route53
- **Benefit**: Geographic routing + fast configuration changes

### 2. Traffic Shaping and Load Shedding

- **Solution**: Enhanced Zuul with throttling and failover modes
- **Benefit**: Protection against thundering herd during failover

### 3. Asynchronous Data Replication

- **Solution**: Cassandra multi-DC + EvCache invalidation
- **Benefit**: Eventually consistent data across regions

### 4. Multi-Regional Deployment

- **Solution**: Mimir workflow automation
- **Benefit**: Consistent deployments across 6 environments

### 5. Validation and Testing

- **Solution**: Graduated chaos engineering (Monkey → Gorilla → Kong)
- **Benefit**: Proactive identification and resolution of failure scenarios

## Key Takeaways

1. **Proactive resilience**: Build failure handling into architecture from the start
2. **Gradual complexity**: Start with zone-level resilience, then region-level
3. **Comprehensive testing**: Regular chaos engineering validates assumptions
4. **Automation is critical**: Manual failover is too slow for modern scale
5. **Data consistency**: Asynchronous replication works for most use cases when properly implemented
6. **Operational tooling**: Effective DNS, traffic shaping, and deployment automation are essential
7. **Team coordination**: Non-technical complexity often exceeds technical challenges

## Next Steps (Phase 2)

Netflix's continued focus areas:

- **Operational automation**: Minimize manual steps in failover process
- **Decision time reduction**: Faster detection and failover initiation
- **Traffic migration speed**: Reduce time to complete failover
- **Partial failure handling**: Deal with intermittent slowness/errors (harder than complete failures)
- **Latency Monkey**: Inject latencies and errors at various frequencies

## Architecture Impact

This Active-Active architecture allows Netflix to maintain their 99.99% availability target even when facing complete regional failures, which is essential for their global streaming service serving millions of concurrent users.

The system demonstrates that with proper architectural principles (isolation, redundancy, asynchronous replication) and comprehensive tooling (DNS control, traffic shaping, deployment automation, chaos testing), large-scale services can achieve exceptional resilience without sacrificing performance or user experience.
