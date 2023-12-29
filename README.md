## Getting Started

### Prerequisites
Ensure you have Docker installed on your system to run the application in containers. The database connection parameters and necessary migration scripts are already configured, so you will likely only need to execute Docker commands to get everything up and running.

### Setting Up the Database
Most of the database setup is pre-configured. However, in case the database is not initialized or migrations are not applied, follow these steps:

1. **Initialize Alembic (only if not already initialized):
   ```bash
   docker-compose exec quart_app alembic init alembic
   ```

2. **Run Migrations** (only if not already done):
   ```bash
   docker-compose exec quart_app alembic revision --autogenerate -m "Initial migration"
   ```

3. **Apply Migrations**:
   ```bash
   docker-compose exec quart_app alembic upgrade head
   ```

### Running the Application
1. **Build the Docker Image**:
   ```bash
   docker-compose build --no-cache
   ```

2. **Start the Docker Containers**:
   ```bash
   docker-compose up
   ```

The application should now be running and accessible at `http://localhost:5000/`.

### Further Work
- **Code Refactoring**: Continual improvement of the codebase for readability and maintainability.
- **Linting and Formatting**: Ensuring code hygiene and consistency using linting and formatting tools.
- **Unit Tests**: Development of unit tests to validate the correctness of the code.
- **Activity Endpoint Optimization**: Implementing keyset or cursor-based pagination for the activity endpoint.
- **Server-Side Caching for Log Data**: Adding caching mechanisms to optimize performance for log data retrieval.