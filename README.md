# GPT-Flask
Flask HTTP server for API calls to OpenAI.

## Development setup
From the project root, create a virtual environment and activate it:

### Windows PowerShell
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project dependencies:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Startup
To start the server from the project root:
```bash
flask run
```

For debug mode (saves scans to disk):
```bash
flask run --debug
```

## Configuration
Request logging is disabled by default. To enable writing request/response logs,
set this in your `.env` file:
```env
ENABLE_REQUEST_LOGGING=true
```

Caching is enabled by default. To disable cache reads/writes, set this in your
`.env` file:
```env
ENABLE_CACHING=false
```

## Routes

### GET /
Returns a simple health check page:
```text
<p>Hello, World!</p>
```

### GET /test
Runs a small OpenAI model smoke test and returns the model output as plain text.

### POST /scene-inference
Classifies the scene from uploaded images and a JSON metadata payload, and also returns the ambient temperature associated with the scene.

Expected request format:
- Form field: `jsonText`
- JSON body should include at least:
  - `name` (scene name, optional but used in the prompt)
  - `ambient_temperature` (used in the scene metadata and returned with the result)
- Uploaded files:
  - `scene` images, exactly 4 files

Example:
```http
POST /scene-inference
Content-Type: application/x-www-form-urlencoded

jsonText={"name":"kitchen", "ambient_temperature":20}
```

Response:
- Plain text response with the inferred scene category and ambient temperature
- HTTP 200 on success
- HTTP 400 when `jsonText` is missing or the image count is incorrect

### POST /object-material-inference
Infers object material information from context and isolated object images + JSON metadata.

Expected request format:
- Form field: `jsonText`
- JSON body should include fields such as:
  - `name`
  - `scale`
  - `size`
  - `ambient_temperature`
  - `scene_category`
- Uploaded files:
  - `context` images, exactly 8 files
  - `iso` images, exactly 8 files

Example:
```http
POST /object-material-inference
Content-Type: application/x-www-form-urlencoded

jsonText={"name":"chair","scene_category":"kitchen","scale":"medium","size":"large","ambient_temperature":21}
```

Response:
- JSON response containing the inferred object material details
- HTTP 200 on success
- HTTP 400 when required input is missing or image counts are wrong