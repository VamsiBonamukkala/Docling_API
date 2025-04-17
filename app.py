from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import tempfile
from docling_parser import pdf_extract_docling,load_test_pdf  # Replace with the correct module path
from langchain_text_splitters import RecursiveCharacterTextSplitter
import uvicorn
import os
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Create the splitter instance
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=100,
    separators=["\n\n", "\n", ".", " ", ""]
)
app = FastAPI(title="Docling PDF Extractor")

# Optional: allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    # Load the test PDF to trigger model downloads
    load_test_pdf()
    # Perform any other startup tasks here
    print("Startup event: Test PDF loaded to trigger model downloads.")

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    # Save the uploaded file to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file_path = Path(tmp.name)
        shutil.copyfileobj(file.file, tmp)

    try:
        text_list, tables_list, images_list = pdf_extract_docling(str(file_path), text_splitter)
        # Serialize tables (pandas DataFrame) into JSON
        serialized_tables = [
            {"data": df.to_dict(orient="records"), "metadata": meta}
            for df, meta in tables_list
        ]

        return JSONResponse(content={
            "text": text_list,
            "tables": serialized_tables,
            "images": images_list
        })

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        file_path.unlink(missing_ok=True)  # Clean up temp file

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8998, workers=1)
