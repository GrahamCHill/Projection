# CV Quality Scanner
## About
This is a simple tool to scan CVs for quality and compliance with best practices. It checks for common issues such as 
missing sections, formatting problems, and readability. It is designed to help job seekers improve their CVs and 
increase their chances of getting hired. It can also be used by recruiters to quickly assess the quality of a CV, or by
companies to ensure that applicant CVs are compliant with their standards.

## Usage
To use the CV Quality Scanner, you can run the shell or batch script provided in the repository. The script will load a
frontend interface that allows you to upload a CV file and scan it for quality issues. The script will also provide
feedback on how to improve the CV and increase its chances of getting hired.

## Requirements
The CV Quality Scanner requires that you have signed up for an account with Groq (or another AI provider) and have
obtained an API key. You will need to set the `GROQ_API_KEY` environment variable to your API key before running
the script. You can do this by creating a `.env` file in the project root directory with the following content:
```
GROQ_API_KEY=your_api_key_here

# Database Configuration (optional)
DB_TYPE=sqlite  # Options: sqlite, mysql
```
Note that there is a `.env.sample` file in the project root directory that you can use as a template.

### Database Configuration
The application supports two database backends:
1. **SQLite** (default) - A file-based database that requires no additional setup
2. **MySQL** - A more robust database system for production environments

To configure the database, you can set the following environment variables in your `.env` file:
```
# Database Configuration
# Options: sqlite, mysql
DB_TYPE=sqlite

# SQLite Configuration (used when DB_TYPE=sqlite)
SQLITE_PATH=sqlite:///./cv_scanner.db

# MySQL Configuration (used when DB_TYPE=mysql)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=password
DB_NAME=cv_scanner

# S3 Storage Configuration
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=cv-documents
USE_MOCK_S3=true

# Vector Database Configuration
VECTOR_DB_URL=http://qdrant:6333

# GitHub Configuration
GITHUB_TOKEN=your_github_token_here
GITHUB_ENTERPRISE_URL=
GITHUB_POLLING_INTERVAL=600
GITHUB_USERS=username1,username2
GITHUB_ORGANIZATIONS=org1,org2
```

For more detailed information about the database system, please refer to the [Database Documentation](./py_backend_logic/DATABASE.md).

You will also need to have Python 3.8 or higher installed on your system, as well as the required Python packages.

### Core Dependencies
- annotated-types==0.7.0
- anyio==4.9.0
- certifi==2025.7.14
- distro==1.9.0
- exceptiongroup==1.3.0
- fastapi==0.116.1
- groq==0.30.0
- h11==0.16.0
- httpcore==1.0.9
- httpx==0.28.1
- idna==3.10
- pydantic==2.11.7
- pydantic_core==2.33.2
- python-dotenv==1.1.1
- sniffio==1.3.1
- sqlalchemy==2.0.27
- pymysql==1.1.0
- starlette==0.47.2
- typing-inspection==0.4.1
- typing_extensions==4.14.1
- uvicorn==0.30.1

### S3 Storage Dependencies
- boto3==1.34.69
- botocore==1.34.69
- s3fs==2024.6.0

### Vector Database Dependencies
- numpy==1.26.4
- qdrant-client==1.7.3
You can install the required packages by running the following command in the `py_backend_logic` directory:
```
pip install -r requirements.txt
```

You will also need a web browser to access the frontend interface, and `node` and `npm` to run the frontendserver.
You can install `node` and `npm` from the official website: https://nodejs.org/

## Docker
If you prefer to run the CV Quality Scanner in Docker containers, you can use the provided docker-compose.yml file. 
This will set up the backend, frontend, and optionally a MySQL database.

### Running with Docker Compose
To start all services, run the following command in the root directory of the repository:
```
docker-compose up -d
```

### Configuration with Docker
The docker-compose.yml file includes configuration for several services:

#### Database Configuration
- **SQLite (Default)**: No additional configuration needed
- **MySQL**: To use MySQL instead of SQLite, set the `DB_TYPE` environment variable to `mysql` in your `.env` file

#### S3-Compatible Storage
The application includes a toggleable S3-compatible storage service using MinIO:
- **Mock S3 (Default)**: Uses MinIO as a local S3-compatible storage (use username and password `minioadmin` if using 
default configuration.)
- **Real S3**: Can be configured to use a real AWS S3 bucket by setting `USE_MOCK_S3=false` and providing your AWS credentials

#### Vector Database
The application includes a vector database service using Qdrant for storing and searching document embeddings.

Example `.env` file for Docker with all services:
```
GROQ_API_KEY=your_api_key_here

# Database Configuration
DB_TYPE=mysql
DB_PASSWORD=your_secure_password

# S3 Storage Configuration
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=cv-documents
USE_MOCK_S3=true

# Vector Database Configuration
VECTOR_DB_URL=http://qdrant:6333
```

This will start the CV Quality Scanner with the backend on port 8000 and the frontend on port 80. You can access the frontend interface by opening your web browser and navigating to `http://localhost`.

### Testing the Integration

To test the integration of S3 storage and vector database, you can run the provided test script:

```bash
cd py_backend_logic
python tests/test_integration.py
```

This script will:
1. Check if all services are running correctly
2. Test S3 storage operations (upload, list, download, delete)
3. Test vector database operations (store, search, retrieve, delete)
4. Test the integration API endpoints

Make sure all Docker containers are running before executing the test script.

## Integration API Endpoints

The application provides several API endpoints for interacting with the S3 storage and vector database:

### Status Endpoint
- `GET /api/integration/status`: Get the status of the integration services

### CV Document Operations
- `POST /api/integration/upload-cv`: Upload a CV document, store it in S3, and create a vector embedding
- `GET /api/integration/list-cvs`: List CV documents stored in the vector database
- `GET /api/integration/get-cv/{document_id}`: Get a CV document by ID
- `POST /api/integration/search-similar`: Search for similar CV documents based on a text query
- `DELETE /api/integration/delete-cv/{document_id}`: Delete a CV document by ID

### S3 Storage Toggle
- `GET /api/integration/toggle-mock-s3`: Toggle between mock S3 and real S3 (for demonstration purposes)

## GitHub Repository Management

The application includes a GitHub repository management system that allows you to:
1. Poll GitHub repositories (personal or enterprise) at regular intervals
2. Store repository information in the database
3. Tag repositories and organize them into projects
4. Search and filter repositories

### Configuration

To use the GitHub repository management features, you need to configure the following environment variables:

```
# GitHub Configuration
# Personal access token with repo scope
GITHUB_TOKEN=your_github_token_here
# GitHub Enterprise URL (leave empty for github.com)
GITHUB_ENTERPRISE_URL=
# Polling interval in seconds (default: 600 = 10 minutes)
GITHUB_POLLING_INTERVAL=600
# Comma-separated list of GitHub usernames to monitor
GITHUB_USERS=username1,username2
# Comma-separated list of GitHub organizations to monitor
GITHUB_ORGANIZATIONS=org1,org2
```

### GitHub API Endpoints

#### Repository Management
- `GET /api/github/repositories`: List all repositories
- `GET /api/github/repositories/{repo_id}`: Get a repository by ID
- `DELETE /api/github/repositories/{repo_id}`: Delete a repository by ID

#### Tag Management
- `GET /api/github/tags`: List all tags
- `POST /api/github/tags`: Create a new tag
- `GET /api/github/tags/{tag_id}`: Get a tag by ID
- `DELETE /api/github/tags/{tag_id}`: Delete a tag by ID
- `POST /api/github/repositories/{repo_id}/tags/{tag_id}`: Add a tag to a repository
- `DELETE /api/github/repositories/{repo_id}/tags/{tag_id}`: Remove a tag from a repository

#### Project Management
- `GET /api/github/projects`: List all projects
- `POST /api/github/projects`: Create a new project
- `GET /api/github/projects/{project_id}`: Get a project by ID
- `DELETE /api/github/projects/{project_id}`: Delete a project by ID
- `POST /api/github/repositories/{repo_id}/projects/{project_id}`: Add a repository to a project
- `DELETE /api/github/repositories/{repo_id}/projects/{project_id}`: Remove a repository from a project

#### Polling Control
- `GET /api/github/polling/status`: Get the status of the GitHub polling scheduler
- `POST /api/github/polling/start`: Start the GitHub polling scheduler
- `POST /api/github/polling/stop`: Stop the GitHub polling scheduler
- `POST /api/github/polling/poll-now`: Trigger an immediate poll of GitHub repositories
- `POST /api/github/polling/poll-user/{username}`: Poll repositories for a specific user
- `POST /api/github/polling/poll-organization/{org_name}`: Poll repositories for a specific organization
- `GET /api/github/rate-limit`: Get GitHub API rate limit information

### Example Usage for GitHub API

#### Creating a Tag
```bash
curl -X POST "http://localhost:8000/api/github/tags" \
  -H "Content-Type: application/json" \
  -d '{"name": "Frontend", "description": "Frontend repositories", "color": "#FF5733"}'
```

#### Adding a Repository to a Project
```bash
curl -X POST "http://localhost:8000/api/github/repositories/1/projects/1"
```

#### Polling Repositories for a Specific User
```bash
curl -X POST "http://localhost:8000/api/github/polling/poll-user/username"
```

#### Getting Polling Status
```bash
curl -X GET "http://localhost:8000/api/github/polling/status"
```

### Example Usage for Integration API

#### Uploading a CV
```bash
curl -X POST "http://localhost:8000/api/integration/upload-cv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/your/cv.pdf" \
  -F "title=My CV" \
  -F "description=Software Engineer CV"
```

#### Searching for Similar CVs
```bash
curl -X POST "http://localhost:8000/api/integration/search-similar" \
  -H "Content-Type: application/json" \
  -d '{"query": "software engineer with python experience"}'
```

## Contributing
If you want to contribute to the CV Quality Scanner, you can fork the repository and create a pull request. You can 
also report issues or suggest features by opening an issue in the repository.

## License
The CV Quality Scanner is licensed under the GNU Lesser General Public License (LGPL) v3.0. See the LICENSE file for more details.

### Acknowledgements
This project is inspired by a project created by my one of my superiors at work, who used it to scan CVs for quality
and compliance with best practices. I have just adapted it to have a more user-friendly interface and to be more flexible
in regard to the extensibility of both the frontend and backend. 

This project uses the Grok AI API to perform the CV quality checks. Grok is a powerful AI provider that offers a wide
range of AI services, including natural language processing, computer vision, and more. You can learn more about Grok
and sign up for an account at https://grok.com/.


