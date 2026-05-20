import os
import pandas as pd

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import FileResponse

from classify import classify

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Log Classification API Running"}


@app.post("/classify/")
async def classify_logs(file: UploadFile):

    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="File must be a CSV."
        )

    try:

        # Read CSV
        df = pd.read_csv(file.file)

        # Validate columns
        required_columns = {"source", "log_message"}

        if not required_columns.issubset(df.columns):

            raise HTTPException(
                status_code=400,
                detail="CSV must contain 'source' and 'log_message' columns."
            )

        # Classification
        df["target_label"] = classify(
            list(zip(df["source"], df["log_message"]))
        )

        print(df.head())

        # Ensure resources directory exists
        os.makedirs("resources", exist_ok=True)

        output_file = "resources/output.csv"

        # Save results
        df.to_csv(output_file, index=False)

        print("File saved:", output_file)

        return FileResponse(
            output_file,
            media_type="text/csv",
            filename="classified_logs.csv"
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        file.file.close()