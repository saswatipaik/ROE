from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pdfplumber
import io

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_pdf(file: UploadFile = File(...)):
    contents = await file.read()

    try:
        with pdfplumber.open(io.BytesIO(contents)) as pdf:
            total_sum = 0
            for page in pdf.pages:
                table = page.extract_table()
                if not table:
                    continue

                headers = [col.strip().lower() for col in table[0]]
                try:
                    prod_idx = headers.index("product")
                    total_idx = headers.index("total")
                except ValueError:
                    continue  # Skip if headers not found

                for row in table[1:]:
                    if row[prod_idx].strip().lower() == "thingamajig":
                        try:
                            total_sum += int(row[total_idx])
                        except (ValueError, TypeError):
                            continue

        return {"sum": total_sum}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
