# Debug-Bridge-Server
* Provide interfaces to communicate between debug bridge server and client.
* Set up this project on: 11/15/2024.

### 1. Installation.

* __python__: recommend v3.11.x, such as v3.11.7

### 2. Set up.

```commandline
git clone https://github.com/dylanz666/debug-bridge.git
```

```commandline
pip install -r requirements.txt
```

### 3. Start server.

* __default__:

```commandline
uvicorn main:app
```

* __assign ip and port__:

```commandline
uvicorn main:app --host 0.0.0.0 --port 8001 --log-config log-config.yaml
```

* __by python command__:

```commandline
python main.py 8001
```

### 4. Swagger UI.

* __default__:

```commandline
# open below url on your browser
https://127.0.0.1:8000/docs
```

* __port assigned__:

```commandline
# open below url on your browser with your own port

https://127.0.0.1:<your port>/docs
```

### 5. I'm also preparing a web page client to show some details and agent's output.
* __Please refer to__: https://github.com/dylanz666/debug-bridge-client

### 6. Reference.
* __FastAPI__: https://fastapi.tiangolo.com/tutorial/
