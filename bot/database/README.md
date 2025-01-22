# PostgreSQL Dockerized Database Setup

## Prerequisites

1. Install [Docker](https://www.docker.com/).
2. Install [Docker Compose](https://docs.docker.com/compose/install/).

---

## Steps to Run the Database

### Step 1: Start the Database
Run the following command to start the PostgreSQL container:
```bash
docker-compose up --build
```

### Step 2: Stop the Database
To stop the database container, run:
```bash
docker-compose down
```
### Step 3: Access the Database
```bash
psql -h localhost -p 5433 -U myuser -d heymax_db
```

### Step 4: Verify the Schema
#### 1. List all tables to confirm the schema was applied:
```bash
\dt
```
#### 2. The following tables should be present:
- Users
- Channels
- ScrapedMessages
- BotInteractions