# Scaling SSE Servers

Server-Sent Events (SSE) allow a server to push real-time updates to clients over long-lived HTTP connections. When designing a system to support many concurrent SSE connections, it's important to understand the factors that limit scalability and how to estimate the number of servers required.

## How Many SSE Connections Can a Single Machine Handle?

The number of concurrent SSE connections a single server can handle depends on several factors:

### 1. File Descriptors

- **What are file descriptors?**
  - In Unix-like operating systems, a file descriptor is an integer that uniquely identifies an open file, socket, or network connection for a process.
  - Every open SSE connection uses a file descriptor.
- **Default limits:**
  - By default, a process might be limited to 1024 open file descriptors (check with `ulimit -n`).
  - This limit can be increased (e.g., to 100,000+) by tuning system settings.
- **Example:**
  - If your server has a file descriptor limit of 10,000, you cannot have more than 10,000 open SSE connections, regardless of available memory or CPU.
  - To check and set the limit:
    ```sh
    ulimit -n           # Show current limit
    ulimit -n 100000    # Set new limit (for the shell/session)
    ```
  - For permanent changes, edit `/etc/security/limits.conf` (Linux) or use `launchctl limit maxfiles` (macOS).

### 2. Threaded vs. Evented Web Servers

- **Threaded Servers:**
  - Each connection is handled by a separate thread.
  - Examples: Traditional Java servers (Tomcat), Python WSGI servers (Gunicorn with default workers).
  - **Limitation:** Each thread consumes memory and CPU. Most servers can only handle a few hundred to a few thousand threads before running out of resources.
  - **Example:** If each thread uses 2 MB of RAM, 1,000 connections = 2 GB RAM just for threads.
- **Evented (Event-driven) Servers:**
  - Use a single (or a few) threads to handle many connections asynchronously.
  - Examples: Node.js, Go, Python with asyncio, Nginx (as a reverse proxy).
  - **Advantage:** Can handle tens of thousands of connections with minimal memory overhead per connection (often just a few KB).
  - **Example:** Node.js or Go server with 8 GB RAM can often handle 50,000–100,000 SSE connections, assuming proper tuning.

### 3. Memory and CPU

- Each connection uses some memory (buffer, state). Lightweight evented servers keep this to a minimum.
- If your application does heavy computation per connection, CPU can become a bottleneck.

### 4. Network Bandwidth

- If you send frequent or large messages, bandwidth may limit scalability.

## Example Calculation

Suppose you want to support 100,000 concurrent SSE clients:

- **Assume:** Each connection uses 50 KB RAM (buffer, state, overhead).
- **Total RAM needed:** 100,000 × 50 KB = ~5 GB (just for connections).
- **Add OS/app overhead:** Plan for 8–16 GB RAM per server.
- **File descriptors:** Set `ulimit -n` to at least 100,000.
- **CPU:** Minimal if just relaying events, more if processing per connection.

A modern 8–16 GB RAM server with an evented server (Node.js, Go, etc.) can handle 50,000–100,000 SSE connections.

## How Many Servers Do You Need?

**Formula:**

```
Number of servers = ceil(Total desired connections / Connections per server)
```

- If you need 500,000 concurrent connections, and each server can handle 50,000:
  - 500,000 / 50,000 = 10 servers

## Practical Tips

- **Load Balancing:** Use a load balancer that supports sticky sessions (so each client stays on the same server).
- **Health Checks:** Monitor connection counts, memory, and CPU.
- **Horizontal Scaling:** Add more servers as needed.
- **Graceful Restarts:** Handle reconnections smoothly.

## Summary Table

| Server Type            | Typical Connections | Notes                 |
| ---------------------- | ------------------- | --------------------- |
| Node.js/Go/Nginx       | 10,000–100,000+     | Evented, lightweight  |
| Java/Python (threaded) | 500–2,000           | Thread/memory limited |

## References

- [Scaling SSE: How many connections can you handle? (Stack Overflow)](https://stackoverflow.com/questions/5195452/how-many-concurrent-http-connections-can-a-server-handle)
- [Nginx SSE Tuning](https://www.nginx.com/blog/websocket-nginx/)
- [Node.js SSE Example](https://www.digitalocean.com/community/tutorials/nodejs-server-sent-events-build-realtime-app)
