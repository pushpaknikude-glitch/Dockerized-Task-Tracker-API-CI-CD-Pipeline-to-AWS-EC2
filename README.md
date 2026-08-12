# Task Tracker API — Dockerized CI/CD Pipeline to AWS EC2

A small Flask REST API backed by Redis, containerized with Docker, and
automatically built and deployed to an AWS EC2 instance via GitHub Actions
on every push to `main`.

This project was built to demonstrate a complete, practical DevOps workflow:
**source control → containerization → CI/CD automation → cloud deployment.**

## Architecture

```
 Developer
     │  git push (main)
     ▼
 GitHub Repo ───► GitHub Actions
                     │
                     ├─► Build Docker image
                     ├─► Push image to Docker Hub
                     └─► SSH into EC2 ─► pull latest image ─► restart container
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │   AWS EC2        │
                                     │  ┌────────────┐  │
                                     │  │ task-tracker│  │
                                     │  │  (Flask)    │──┼──► port 5000
                                     │  └─────┬──────┘  │
                                     │        │         │
                                     │  ┌─────▼──────┐  │
                                     │  │   Redis    │  │
                                     │  └────────────┘  │
                                     └─────────────────┘
```

## Tech Stack

- **App**: Python / Flask
- **Data store**: Redis
- **Containerization**: Docker, docker-compose
- **CI/CD**: GitHub Actions
- **Cloud**: AWS EC2 (free tier)
- **Registry**: Docker Hub

## API Endpoints

| Method | Endpoint       | Description                          |
|--------|----------------|---------------------------------------|
| GET    | `/`            | API info                              |
| GET    | `/health`      | Health check (verifies Redis connection) |
| GET    | `/tasks`       | List all tasks                        |
| POST   | `/tasks`       | Create a task — body: `{"title": "..."}` |
| DELETE | `/tasks/<id>`  | Delete a task by id                   |

## Run Locally

Requires Docker and docker-compose.

```bash
git clone https://github.com/<your-username>/task-tracker.git
cd task-tracker
docker compose up --build
```

App will be available at `http://localhost:5000`.

Test it:

```bash
curl -X POST http://localhost:5000/tasks -H "Content-Type: application/json" -d '{"title":"Learn Docker"}'
curl http://localhost:5000/tasks
curl http://localhost:5000/health
```

## Deployment (CI/CD to AWS EC2)

### 1. Launch an EC2 instance
- Ubuntu 22.04, t2.micro (free tier)
- Security group: allow inbound TCP 22 (SSH) and 5000 (app)
- Install Docker on the instance:
  ```bash
  sudo apt update && sudo apt install -y docker.io
  sudo usermod -aG docker ubuntu
  ```

### 2. Create a Docker Hub repository
Create a repo named `task-tracker` (or update the image name in the workflow).

### 3. Add GitHub Secrets
In your repo → Settings → Secrets and variables → Actions, add:

| Secret               | Value                                      |
|-----------------------|--------------------------------------------|
| `DOCKERHUB_USERNAME`  | Your Docker Hub username                    |
| `DOCKERHUB_TOKEN`     | Docker Hub access token (not your password) |
| `EC2_HOST`            | Public IP or DNS of your EC2 instance       |
| `EC2_SSH_KEY`         | Contents of your EC2 `.pem` private key     |

### 4. Push to main
```bash
git add .
git commit -m "Deploy task tracker"
git push origin main
```

Watch the pipeline run under the **Actions** tab. Once green, your app is
live at `http://<EC2_HOST>:5000`.

## Project Structure

```
task-tracker/
├── app/
│   ├── app.py
│   └── requirements.txt
├── .github/
│   └── workflows/
│       └── deploy.yml
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
└── README.md
```

## What This Project Demonstrates

- Writing clean, containerized application code
- Multi-container orchestration with docker-compose
- Building CI/CD pipelines with GitHub Actions
- Managing secrets securely
- Provisioning and configuring cloud infrastructure (AWS EC2, security groups)
- Automated, zero-touch deployment on every push

## License

MIT
