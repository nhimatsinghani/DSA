# Meta Product Architecture / Design Interview Study Guide

## 1. What is the Product Architecture/Design Interview?

- **Focus:** Designing a user-facing product or API at scale, considering end-to-end experience, not just backend scalability.
- **Goal:** Assess your ability to build software solutions with a strong product mindset, balancing user needs, technical trade-offs, and scalable architecture.
- **Typical Prompts:** Design Facebook News Feed, Ticketmaster, a chat app, ride-sharing backend, Dropbox, etc.

**References:**

- [DesignGurus: Mastering Meta’s Product Design Interview](https://www.designgurus.io/blog/mastering-metas-product-design-interview)
- [IGotAnOffer: How to crack the Meta Product Architecture interview](https://igotanoffer.com/en/advice/meta-product-architecture-interview)
- [Hello Interview: Meta System vs Product Design](https://www.hellointerview.com/blog/meta-system-vs-product-design)

---

## 2. Key Differences: Product Architecture vs. System Design

| Aspect               | Product Architecture Interview             | System Design Interview                 |
| -------------------- | ------------------------------------------ | --------------------------------------- |
| **Focus**            | User-facing product, APIs, UX, data models | Backend scalability, infra, reliability |
| **Depth**            | Broader, holistic, product-centric         | Deep technical, infra-centric           |
| **Open-endedness**   | More open, creative, user scenarios        | More established best practices         |
| **Client-Server**    | Must consider client integration, flows    | Client often out of scope               |
| **API & Data Model** | Central to the discussion                  | Often secondary to infra                |

---

## 3. Interview Format & Stages

- **45 minutes total**
  1. **Clarify requirements (5 min):** Define users, use cases, MVP, constraints.
  2. **High-level design (10 min):** Major components, data flow, storage, APIs.
  3. **API & Data modeling (10 min):** Endpoints, data schema, user-centric design.
  4. **Deep dive & trade-offs (15 min):** Focus on critical component, discuss alternatives, edge cases, scaling.
  5. **Wrap-up (5 min):** Summarize, discuss improvements, answer Q&A.

**Tip:** Use a repeatable framework: Clarify → High-level → Deep dive → Summarize.

---

## 4. Example Questions

- Design Facebook News Feed
- Design Ticketmaster (event ticketing)
- Design a chat/messaging app
- Design a ride-sharing backend
- Design Dropbox/Google Drive
- Design the UX and APIs for a new feature (e.g., personalized feed)
- Design Leetcode

**Practice:** Use these prompts to simulate interviews, draw diagrams, and time yourself.

---

## 5. Evaluation Criteria

- **User-focused product thinking:** Do you clarify user needs, use cases, and product goals?
- **Solution design & coverage:** Is your architecture complete, covering all scenarios?
- **API design & data modeling:** Are your APIs clean, robust, and user-centric? Is your data model scalable?
- **Trade-offs & reasoning:** Do you discuss alternatives and justify your choices?
- **Technical excellence:** Do you address scale, reliability, security, and edge cases?
- **Front-end/back-end integration:** Do you explain client-server flows and integration?
- **Communication & structure:** Are your explanations clear, logical, and collaborative?

---

## 6. Preparation Strategies

- **Review fundamentals:** Web app architecture, REST/GraphQL APIs, SQL/NoSQL, caching, load balancing, security.
- **Learn a framework:** Always start with requirements, then high-level, then deep dive, then wrap-up.
- **Practice with real scenarios:** Use example questions, simulate interviews, draw diagrams (Excalidraw/whiteboard).
- **Cover breadth and depth:** Outline the whole system, then deep dive on a critical part.
- **Sharpen product sense:** Reverse-engineer real apps, read engineering blogs (Meta, Uber, Dropbox, etc.).
- **Focus on communication:** Practice explaining your design out loud, get feedback.
- **Time management:** Practice under time constraints (35 min for design, 5 min for wrap-up).
- **Mock interviews:** Practice with peers or coaches, get feedback, iterate.

**Recommended Books/Resources:**

- [Designing Data-Intensive Applications (Martin Kleppmann)](https://dataintensive.net/)
- [System Design Interview (Alex Xu)](https://www.amazon.com/System-Design-Interview-insiders-Second/dp/B08CMF2CQF)
- [Grokking the System Design Interview (DesignGurus)](https://www.designgurus.io/course/system-design)
- [Meta Engineering Blog](https://engineering.fb.com/)

---

## 7. Deep Dives on Key Topics

### A. Data Ownership

- **Definition:** Who controls, accesses, and manages data in your system? How is user data protected, portable, and private?
- **Considerations:**
  - User consent and privacy (GDPR, CCPA)
  - Data portability and sovereignty
  - Data deletion and retention policies
  - Multi-tenant data isolation
- **Further Reading:**
  - [The Age of Data Sovereignty (Hypercube)](https://github.com/alexotsu/hypercube-spec)
  - [Towards Data Neutrality (Reboot)](https://joinreboot.org/p/rhizome)
  - [Rhizome Proposal](https://jzhao.xyz/thoughts/Rhizome-Proposal)

### B. Protocols

- **Definition:** Rules and standards for communication between system components (e.g., HTTP, WebSockets, gRPC, custom protocols).
- **Common Protocols:**
  - HTTP/HTTPS (REST APIs)
  - WebSockets (real-time communication)
  - Server-Sent Events (SSE)
  - gRPC (efficient, strongly-typed RPC)
  - MQTT (IoT messaging)
- **Design Considerations:**
  - When to use polling vs. pushing (WebSockets/SSE)
  - Security (TLS, authentication)
  - Backward/forward compatibility
- **Further Reading:**
  - [Web Data Protocols Proposal](https://gist.github.com/pfrazee/860f2d137ef001a89da4b3959e259d58)
  - [MDN: Protocols](https://developer.mozilla.org/en-US/docs/Web/HTTP/Protocols)
  - [gRPC vs REST](https://www.designgurus.io/blog/rest-graphql-grpc-system-design)

### C. Data Formats

- **Definition:** How data is structured and exchanged between components (e.g., JSON, XML, Protocol Buffers, Avro).
- **Common Formats:**
  - JSON (ubiquitous, human-readable)
  - XML (older, verbose)
  - Protocol Buffers (protobuf, efficient, binary)
  - Avro, Thrift (other binary formats)
- **Design Considerations:**
  - Human-readability vs. efficiency
  - Schema evolution and versioning
  - Interoperability between systems
- **Further Reading:**
  - [Google Protocol Buffers](https://developers.google.com/protocol-buffers)
  - [JSON vs Protobuf vs Avro](https://www.baeldung.com/cs/json-vs-protobuf-vs-avro)
  - [MDN: JSON](https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Objects/JSON)

### D. Client-Server Design

- **Definition:** How clients (web/mobile apps) interact with servers (APIs, backend services).
- **Patterns:**
  - Request/response (REST)
  - Real-time (WebSockets, SSE)
  - GraphQL (flexible queries)
  - Offline-first (sync, local storage)
- **Design Considerations:**
  - Latency and user experience
  - Error handling and retries
  - Security (auth, rate limiting)
  - Versioning and backward compatibility
  - Mobile/web constraints (bandwidth, battery)
- **Further Reading:**
  - [Client-Server Model (Wikipedia)](https://en.wikipedia.org/wiki/Client%E2%80%93server_model)
  - [MDN: Client-Server Overview](https://developer.mozilla.org/en-US/docs/Learn/Server-side/First_steps/Client-Server_overview)
  - [Polling vs WebSockets vs SSE](https://ably.com/concepts/push-vs-pull)
  - [REST vs GraphQL vs gRPC](https://www.designgurus.io/blog/rest-graphql-grpc-system-design)

---

## 8. Additional Resources & Practice

- [Meta Engineering Blog](https://engineering.fb.com/)
- [Grokking the System Design Interview](https://www.designgurus.io/course/system-design)
- [Hello Interview: Meta Product Architecture](https://www.hellointerview.com/blog/meta-system-vs-product-design)
- [IGotAnOffer: Meta Product Architecture Interview](https://igotanoffer.com/en/advice/meta-product-architecture-interview)
- [YouTube: Meta Product Architecture Interview Overview](https://www.youtube.com/watch?v=jj7NIIkJW4U)
- [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)

---

**Tip:** For each topic, pick 1-2 resources and take notes. Practice by designing real-world products, focusing on user needs, API/data modeling, and client-server flows. Simulate interviews with peers or coaches for feedback.
