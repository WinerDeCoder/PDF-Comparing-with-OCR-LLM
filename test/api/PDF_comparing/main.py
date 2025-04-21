
from mistralai import Mistral
from openai import OpenAI
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import aiofiles
load_dotenv(".env")

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client_openai = OpenAI(api_key = OPENAI_API_KEY)
client = Mistral(api_key=MISTRAL_API_KEY )


from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Union
import json

class Replacement(BaseModel):
    original: str = Field(..., description="The base text from first PDF")
    text: str 
    type:  Literal["replace"]
    
class Addition(BaseModel):
    original: Literal[""]
    text: str
    type: Literal["add"]
    
class Deletion(BaseModel):
    original: Literal[""]
    text: str
    type:  Literal["delete"]
    
class Page(BaseModel):
    page_number: int
    modify_detection: Optional[List[Union['Replacement', 'Addition', 'Deletion']]] 

class Detection_Result(BaseModel):
    page: List[Page]
    modified: Literal["yes", "no"] = Field(..., description="Yes if detect any different, no if not")


async def mistral_ocr(filename, file):
    # Đọc nội dung file từ UploadFile (để đảm bảo nó là bytes)
    #file_bytes = await file.read()
    
    # file.file is a SpooledTemporaryFile, ready to stream
    uploaded = client.files.upload(
        file={
            "file_name": filename,
            "content": file  # ← pass the file-like object directly
        },
        purpose="ocr"
    )
    
    signed_url = client.files.get_signed_url(file_id=uploaded.id)
    
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url.url,
        }
    )
    
    return ocr_response


# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "API is ready!"}


@app.post("/upload-pdf")
async def upload_pdf(file_1: UploadFile = File(...), file_2: UploadFile = File(...)):
    try:
        try:
            # Generate current date and hour
            current_time = datetime.now()
            date_str = current_time.strftime("%Y-%m-%d")
            hour_str = current_time.strftime("%H")

            # Define the base directory
            base_directory = "uploaded_files"
            
            # Create directory paths
            date_directory = os.path.join(base_directory, date_str)
            hour_directory = os.path.join(date_directory, hour_str)

            # Ensure the directories exist
            os.makedirs(hour_directory, exist_ok=True)

            # Generate filenames with a timestamp
            timestamp = current_time.strftime("%Y%m%d%H%M%S")
            file_1_path = os.path.join(hour_directory, f"{timestamp}_1_{file_1.filename}")
            file_2_path = os.path.join(hour_directory, f"{timestamp}_2_{file_2.filename}")

        
            # Save the first file
            async with aiofiles.open(file_1_path, 'wb') as out_file:
                content_1 = await file_1.read()
                await out_file.write(content_1)

            # Save the second file
            async with aiofiles.open(file_2_path, 'wb') as out_file:
                content_2 = await file_2.read()
                await out_file.write(content_2)
        except:
            a = 1
        
        ocr_response_1 = await mistral_ocr(file_1.filename, content_1)
        ocr_response_2 = await mistral_ocr(file_2.filename, content_2)
        
        pages_text = """"""
        
        for index in range(len(ocr_response_1.pages)):
            if index >=4:
                break
            
            page_number = index + 1
            
            pages_text += f"""**This is page number {page_number}**:
- First PDF in Markdown \n\n \"{ocr_response_1.pages[index].markdown}\" 
- Second PDF in Markdown \n\n \"{ocr_response_2.pages[index].markdown}\" 
\n \n
"""      
        
        # Define the messages for the chat
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": """
**Role**: You are a good PDF comparer:

**Detailed Mission**:
- You will receive input text about 2 PDF - all extracted text, in each page.
- These 2 PDF are expected to be the same, but the second one is received from customer, so they could change some thing - what you will detect. 
- You need to detect any different in 3 type: replace, add, delete if exist in each page, if no, leave None. Please follow the given structured to answer.

1. Replacement — A portion of text is replaced by new text.
2. Addition — New text appears in the second document that is not in the first.
3. Deletion — Text present in the first document is removed in the second.

Respond in **JSON format** with the following structure:

```json
{
  "page": [
    {
      "page_number": <number>,
      "modify_detection": [
        {
          "original": "<original text>" if replaced, if "delete" or "add",just leave blank     // only for replacements
          "text": "<new or removed text>",
          "type": "replace" | "add" | "delete"
        }
      ]
    }
  ],
  "modified": "yes" | "no"
}


**Attention**:
- Because the second PDF is scanned, so the overal position may change a bit - lead to Text Extract may not in order from the first, but this should be just a slight change, so do not strict much about the position
- You should care about meaning, sentence level, number
        """
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": pages_text
                    }
                ]
            }
        ]

        completion = client_openai.beta.chat.completions.parse(
            model="gpt-4o",
            messages=messages ,
            response_format=Detection_Result,
        )

        print(completion.choices[0].message.content)

        return JSONResponse(content={
            "status": "success",
            "mistral_response": str(completion.choices[0].message.content) # or uploaded.dict() if supported
        }, status_code = 200)
    
    except Exception as e:
        print(e)
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)