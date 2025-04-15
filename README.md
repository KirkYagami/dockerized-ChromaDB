# Docker:

---
### RESOURCES FOR LEARNING DOCKER:
1. https://medium.com/@techsuneel99/docker-from-beginner-to-expert-a-comprehensive-tutorial-5efec10c82ab
2. https://medium.com/@musinde/docker-fundamentals-8b856f24aeb1
----


## What is Docker?

Docker is a platform that revolutionizes application development and deployment through containerization. Unlike traditional virtual machines that emulate entire operating systems, Docker containers package only the application code, runtime, libraries, and dependencies while sharing the host system's kernel. This architectural difference makes containers significantly more lightweight, faster to start, and more resource-efficient.

### Core Docker Architecture

Docker employs a client-server architecture consisting of:

1. **Docker Engine**: The runtime that builds and runs containers
2. **Docker Daemon**: The background service managing container objects
3. **Docker Client**: The command-line interface users interact with
4. **Docker Registry**: A repository storing Docker images (Docker Hub is the official registry)

### Container vs. Virtual Machine

| Docker Containers       | Virtual Machines         |
| ----------------------- | ------------------------ |
| Share host OS kernel    | Run complete OS copies   |
| Startup in seconds      | Startup in minutes       |
| Size in megabytes       | Size in gigabytes        |
| Lower resource overhead | Higher resource overhead |
| Process-level isolation | Hardware-level isolation |


## Configuration Files in Detail

### Docker Compose File (`docker-compose.yml`)

This orchestration file defines your multi-container application environment using a declarative YAML syntax:

```yaml
version: '3.8'  # Specifies Docker Compose schema version
```

#### ChromaDB Service Configuration
```yaml
services:
  chroma:
    image: chromadb/chroma:latest
    environment:
      - ALLOW_RESET=True
      - ANONYMIZED_TELEMETRY=False
      - CHROMA_SERVER_HOST=0.0.0.0  # Listens on all network interfaces
      - CHROMA_SERVER_PORT=8000
    ports:
      - "8000:8000"  # Maps host port to container port
    volumes:
      - chroma-data:/chroma/chroma  # Named volume for data persistence
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 5s
    restart: unless-stopped  # Automatic restart policy
```

Key aspects:
- **Named volume**: `chroma-data` provides persistent storage across container restarts
- **Healthcheck**: Actively verifies the service is fully operational before dependent services start
- **Restart policy**: Ensures high availability except when manually stopped

#### Application Service Configuration
```yaml
  app:
    build:
      context: .
      dockerfile: Dockerfile
    depends_on:
      chroma:
        condition: service_healthy  # Enhanced dependency management
    environment:
      - CHROMA_HOST=chroma  # Service discovery via Docker networking
      - CHROMA_PORT=8000
    volumes:
      - ./app:/app  # Bind mount for development
```

Key aspects:
- **Build configuration**: Points to a local Dockerfile for custom image building
- **Service dependency**: Uses health-condition based startup sequencing
- **Environment variables**: Uses Docker's internal DNS for service discovery

### Dockerfile

The Dockerfile provides step-by-step instructions to build your application container:

```dockerfile
FROM python:3.11-slim  # Base image with minimal footprint
```
Starts with a minimal Python distribution to reduce attack surface and image size.

```dockerfile
WORKDIR /app  # Set working directory for subsequent commands
```
Creates and sets the default directory for application files.

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
```
Optimizes build caching - dependencies are installed separately from code, meaning dependency layers are cached unless requirements.txt changes.

```dockerfile
COPY app/ .  # Copy application source code
```
Copies application code as the final layer, enabling faster rebuilds during development.

```dockerfile
CMD ["python", "chroma_example.py"]  # Default container command
```
Specifies the entrypoint command when the container starts.

## Docker Networking in Your Setup

Your Docker Compose configuration creates an internal network where:
1. Services can reference each other by name (`chroma` hostname resolves to the ChromaDB container)
2. Only explicitly published ports (8000) are accessible from the host
3. Inter-service communication occurs on an isolated network

## Docker Volume Management

Your configuration uses a named volume `chroma-data` that provides:
1. Data persistence across container restarts/updates
2. Performance advantages over bind mounts
3. Better portability across environments
4. Independent lifecycle management from containers

## Essential Docker Commands

Key commands for working with your Docker setup, in the recommended order for typical operations:

### Initial Setup & Development
```bash
# Build images without starting containers
docker-compose build

# Start services in the foreground with logs visible
docker-compose up

# Start services in the background
docker-compose up -d

# View container logs
docker-compose logs -f
```

### Maintenance Operations
```bash
# Check running container status
docker-compose ps

# Stop all services but keep containers
docker-compose stop

# Stop and remove containers (preserves volumes)
docker-compose down

# Stop and remove containers, networks, AND volumes
docker-compose down -v

# Execute commands inside a running container
docker-compose exec app python -c "print('Hello from inside the container')"

# Restart a specific service
docker-compose restart app
```

### Debugging & Troubleshooting
```bash
# See detailed container information
docker inspect chroma

# Get a shell inside a running container
docker-compose exec app bash

# Check volume data
docker volume ls
docker volume inspect chroma-data

# View container resource usage
docker stats
```

### Production Deployment
```bash
# Validate compose file
docker-compose config

# Deploy stack to Docker Swarm (production mode)
docker stack deploy -c docker-compose.yml chromadb-stack

# Update running services
docker-compose pull && docker-compose up -d
```

By mastering these Docker commands and understanding the configuration files, you'll have complete control over your containerized ChromaDB application environment through its entire lifecycle from development to deployment and maintenance.

![[Pasted image 20250415194658.png]]
