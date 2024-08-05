---
title: Real-time dataset updates
---

# Real-time dataset updates

## Table of Contents

- [Prerequisites](#Prerequisites)
- [Usage](#Usage)
- [Testing](#Testing)
- [Design](#Design)

## Prerequisites

You will need Docker and Docker Compose installed on your system.

## Usage

### Starting the application

To get started with this project, follow these steps:

1. Open any terminal and navigate to the project folder, ie, `cd test-project`.

2. Run `make start` to start the application server. This will internally install the necessary dependencies, 
   create the necessary docker containers, initialize a new dataset/fetch the existing dataset and start the application. 

3. With the application running in a terminal, navigate to http://localhost:8000/ws/dashboard on any browser. This 
   will open up a basic webpage, with a paginated section of the dataset, along with a messages box. 

4. In order to simulate multiple users, open the same page in multiple tabs. You can keep track of the users via 
   a `User ID` field on the webpage.

5. Latency for functions/routes are logged in the terminal on which the application is running.
   

### Interacting with the application

1. Enter any column number (between 0-9) in the text input.

2. Click on the `Update Dataset` button, to simulate updates to the dataset. 

3. The dataset shown on the webpage is refreshed periodically (every 3 seconds), but you can also click on the
   `Fetch Dataset` button to refresh it immediately.

4. You can click on the `Next` or `Previous` buttons to see more rows of the dataset.

5. Updates made by a user/other users will be published in the messages box.


### Stopping the application

1. Run `make stop` to stop the running docker containers, once you have completed interacting with the application.


## Testing

1. Run `make test` to run the tests. This will create a virtual environment, install necessary dependencies and run the tests.


## Design Overview

1. **FastAPI Application**
   - **Purpose:** Acts as the main application server handling HTTP requests and WebSocket connections.
   - **Key Features:**
     - Exposes REST endpoints for managing datasets.
     - Handles WebSocket connections for real-time communication.

2. **DatasetManager**
   - **Purpose:** Manages a simulated dataset stored in Redis.
   - **Functionality:**
     - Initializes a dataset on startup with random data, for 50000 rows and 10 columns.
     - Provides methods to retrieve paginated dataset slices and apply non-deterministic updates asynchronously.

3. **ConnectionManager**
   - **Purpose:** Manages WebSocket connections and facilitates real-time message broadcasting.
   - **Functionality:**
     - Listens to a Redis pub/sub channel for incoming messages.
     - Tracks active WebSocket connections and facilitates connection management (connect, disconnect).
     - Sends messages to individual users or broadcasts messages to all connected users.

4. **Redis**
   - **Purpose:** Acts as a data store for the simulated dataset and as a message broker for WebSocket communication.
   - **Key Components:**
     - Stores dataset columns as Redis hashmaps.
     - Manages active WebSocket connections and facilitates pub/sub messaging for real-time updates.


### Interaction

- **Initialization:**
  - On application startup, `DatasetManager` initializes the dataset in Redis.
  - `ConnectionManager` starts listening to the Redis pub/sub channel for incoming messages.

- **Handling Requests:**
  - **HTTP Requests:** Handled by FastAPI endpoints (`/data`).
    - Retrieve dataset slices.
    - Trigger dataset updates.
  - **WebSocket Requests:** Handled by FastAPI WebSocket endpoint (`/ws`).
    - Establish WebSocket connections.
    - Receive and process real-time messages.

- **Real-time Communication:**
  - Messages published to the Redis pub/sub channel by external processes trigger updates in the dataset.
  - `ConnectionManager` listens to these messages and broadcasts them to all connected WebSocket clients.
