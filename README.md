# API Users and Dogs

This API is built with **Python-FastAPI.**

Implement **Docker** and **JWT** for authentication, with a basic CRUD
for Users and their dogs through the ID relationship in the database, in this case **Postgres.**

## Here is a sample:
**FastAPI** in: http://0.0.0.0/docs

![enter image description here](https://raw.githubusercontent.com/LeidyAcuna/guane-intern-fastapi/dev/images/fastapi-1.png)

**Available authorization**

![enter image description here](https://raw.githubusercontent.com/LeidyAcuna/guane-intern-fastapi/dev/images/fastapi-2.png)

This authorization is required for endpoints **POST** and **PUT**:

![enter image description here](https://raw.githubusercontent.com/LeidyAcuna/guane-intern-fastapi/dev/images/fastapi-3.png)

### User with theirs Dogs

![enter image description here](https://raw.githubusercontent.com/LeidyAcuna/guane-intern-fastapi/dev/images/fastapi-4.png)

**Postgres** in: http://localhost:5050/

![enter image description here](https://raw.githubusercontent.com/LeidyAcuna/guane-intern-fastapi/dev/images/fastapi-5.png)

## Run API:

#### Requirements:
- Python : "^3.8"
- Docker : https://docs.docker.com/get-docker/
- Poetry : https://python-poetry.org/docs/#installation

With the cloned project, inside the terminal follow the commands:

    - cp .env.example .env
    - poetry shell
    - docker-compose up -d
 
 ## JupyterLab

    - docker-compose exec server bash
    - $JUPYTER
