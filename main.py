import io
import uuid
import json
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response
app = FastAPI(
    title="CSV Data Profiling API",
    description="Upload a CSV, inspect its quality, and download it again.",
    version="1.0.0",
)

datasets= {}

@app.get("/")
def read_root():
    return {"message": "CSV profiling API is running"}


@app.post("/api/import")
async def import_csv(file: UploadFile = File(...)):
    
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="only.csv files are allowed.")


    contents = await file.read()
    if len(contents)== 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The CSV has no data.")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="The file is not valid CSV.")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="Could not read file as text.")


    dataset_id= str(uuid.uuid4())
    datasets[dataset_id]= (file.filename, df)


    missing= {col: int(n) for col, n in df.isna().sum().items()}
    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": {col: str(t) for col, t in df.dtypes.items()},
        "missing_values": missing,
        "total_missing": int(df.isna().sum().sum()),
    }

def get_dataset(dataset_id: str):
    """Look up a stored dataset, or raise a 404 error if the ID is unknown."""
    if dataset_id not in datasets:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found. It may never have existed, or the server restarted.",
        )
    return datasets[dataset_id]


def clean_number(value):
    """Convert a Pandas number to a plain float, or None if it is NaN.
    JSON cannot represent NaN, so we send null instead."""
    return None if pd.isna(value) else float(value)



def generate_profile(dataset_id:str):
    filename, df= get_dataset(dataset_id)

    numeric_stats= {}
    for col in df.select_dtypes(include="number").columns:
        s= df[col]
        numeric_stats[col]= {
            "count": int(s.count()),
            "mean": clean_number(s.mean()),
            "min": clean_number(s.min()),
            "max": clean_number(s.max()),
            "std": clean_number(s.std()),
        }

    return {
        "dataset_id": dataset_id,
        "filename": filename,
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "column_names": df.columns.tolist(),
        "data_types": {col: str(t) for col, t in df.dtypes.items()},
        "missing_values": {col: int(n) for col, n in df.isna().sum().items()},
        "total_missing": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "unique_values": {col: int(n) for col, n in df.nunique().items()},
        "numeric_statistics": numeric_stats,
    }

@app.get("/api/profile/{dataset_id}")
def profile_dataset(dataset_id:str):
    return generate_profile(dataset_id)

@app.get("/api/profile/{dataset_id}/download")
def download_profile(dataset_id: str):
    profile_data= generate_profile(dataset_id)

    json_content= json.dumps(
        profile_data,
        indent= 4,
        ensure_ascii=False,
        allow_nan=False
    )

    return Response(
        content= json_content,
        media_type= "application/json",
        headers={
            "Content-Disposition":
                'attachment; filename="dataset_profile.json"'
        }
    )