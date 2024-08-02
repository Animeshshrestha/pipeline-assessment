# Pipeline Assessment Project

This project is designed to fetch, normalize, deduplicate, and visualize data from Qualys and CrowdStrike APIs. The application is scheduled to run at specific times using the `schedule` library.

## Prerequisites

Before you start, make sure you have the following installed on your local machine:

- Docker
- Docker Compose

## Getting Started

### 1. Clone the Repository

Clone this repository to your local machine

### 2. Setting Up Environment Variables

Create the directory structure for storing environment variables:

```bash
  mkdir -p .env/.local/.env
```

Copy the sample environment variables file to the new directory:

```bash
  cp .env.sample .env/.local/.env
```

Edit the .env/.local/.env file to include your specific environment variables:

### 3. Build and Run with Docker Compose

To run this project, run the following command

```bash
  docker compose up --build
```
Note: Depending upon the docker compose version, we have to either use `docker-compose` or `docker compose`. Please take note of this one.

- To run the docker into deattached mode pass -d flag

### 4. Stopping the container

To shutdown the container, run the following command

```bash
  docker compose down
```
Note: Depending upon the docker compose version, we have to either use `docker-compose` or `docker compose`. Please take note of this one.

### 5. Scheduler

The main job is scheduled to run at a specific time every day using the schedule library. The scheduling is defined in the main.py file. Adjust the scheduled time as needed.

### 6. Other Information

- Logs can be accessed via logging folder which are seperated by the date folder which contains the file name with respective to the date.
- Visualized diagrams can be accessed inside the visualized_diagram folder.
- Since the data recieved from the server was limited, i created fake data based on the normalized data pattern and have attached the diagram inside sample_diagram folder.
- **How to scale this system to support millions of objects** answer is written in `scalable_process.txt` file.
