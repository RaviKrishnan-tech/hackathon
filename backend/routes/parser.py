from fastapi import APIRouter, UploadFile, HTTPException
from PyPDF2 import PdfReader
from docx import Document
from typing import Optional
import io

router = APIRouter(prefix="/parse", tags=["Parser"])

@router.post("/")
async def parse_resume(file: UploadFile):
    ext = file.filename.split(".")[-1].lower()
    content = await file.read()  # Read file content as bytes

    try:
        if ext == "pdf":
            pdf_stream = io.BytesIO(content)
            reader = PdfReader(pdf_stream)
            text = "\n".join(
                [page.extract_text() for page in reader.pages if page.extract_text()]
            )
        elif ext == "docx":
            doc_stream = io.BytesIO(content)
            doc = Document(doc_stream)
            text = "\n".join([para.text for para in doc.paragraphs])
        elif ext == "doc":
            # Very basic fallback for legacy DOC files
            text = content.decode(errors="ignore")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    return {"text": text}
