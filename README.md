### 1. Clone the repository

```bash
git clone https://github.com/PolaRizer2835/dataset_profiling.git
```

Navigate into the project directory:

```bash
cd dataset_profiling
```

Alternatively, download the repository as a ZIP file and extract it.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
uvicorn main:app --reload
```

The API server will start at:

http://127.0.0.1:8000

## API Documentation

FastAPI automatically generates interactive API documentation.

Open the following URL in your browser:

**Swagger UI:** http://127.0.0.1:8000/docs

You can upload CSV files, execute API requests, inspect responses, and test the available endpoints directly through your browser.