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
```

For more detailed information about the database system, please refer to the [Database Documentation](./py_backend_logic/DATABASE.md).

You will also need to have Python 3.8 or higher installed on your system, as well as the required Python packages.
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
- starlette==0.47.2
- typing-inspection==0.4.1
- typing_extensions==4.14.1
- uvicorn==0.30.1
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

### Database Configuration with Docker
The docker-compose.yml file includes configuration for both SQLite and MySQL databases:

- **SQLite (Default)**: No additional configuration needed
- **MySQL**: To use MySQL instead of SQLite, set the `DB_TYPE` environment variable to `mysql` in your `.env` file

Example `.env` file for Docker with MySQL:
```
GROQ_API_KEY=your_api_key_here
DB_TYPE=mysql
DB_PASSWORD=your_secure_password
```

This will start the CV Quality Scanner with the backend on port 8000 and the frontend on port 80. You can access the frontend interface by opening your web browser and navigating to `http://localhost`.

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


