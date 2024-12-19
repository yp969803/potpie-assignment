## The project provides the reviewing of the PR's in a github repository

## Local setup
### prerequisite
- python 3.1+
- docker
- github token

Create .env 
```
GITHUB_TOKEN =
```

```
python3 -m venv my_env
source my_env/bin/activate
docker run --name redis-container -d -p 6379:6379 redis
pip install -r requirements.txt
fastapi dev main.py
```