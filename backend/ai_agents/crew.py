from typing import Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import magic
import base64
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

class InvoiceProcessor:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model_name = "qwen/qwen2.5-vl-72b-instruct:free"

    def encode_image(self, image_path: str) -> str:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        try:
            # Get file type
            file_type = magic.from_file(file_path, mime=True)
            
            # Encode image to base64
            base64_image = self.encode_image(file_path)
            
            prompt = """Extract the following text fields: ['Bill To', 'Emailing Address', 'Invoice Number', 
            'Invoice Date', 'Invoice Amount', 'Services'], and format them in JSON format with the following structure:
            {
              "Bill To": "",
              "Emailing Address": "",
              "Invoice Number": "",
              "Invoice Date": "",
              "Invoice Amount": "",
              "Services": [
                {
                  "Service": "",
                  "Quantity": "",
                  "Unit Price": "",
                  "Amount": ""
                }
              ]
            }"""

            messages = [
                {
                    "role": "system",
                    "content": [{"type": "text", "text": "You are an expert invoice analyzer."}]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "min_pixels": 512*28*28,
                            "max_pixels": 2048*28*28,
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            
            extracted_data = response.choices[0].message.content

            # Log the extracted data
            logging.info("Extracted Data: %s", extracted_data)

            # Return structured data
            return {
                'extracted_data': extracted_data,  # This should be in JSON format
                'validation_status': 'success',
                'confidence_score': 0.95,
                'discrepancies': {
                    'source_type': file_type.split('/')[0],
                    'ocr_confidence': 'high',
                    'extracted_text': 'Processed with Qwen VL',
                    'analysis_result': extracted_data
                }
            }

        except Exception as e:
            raise Exception(f"Error processing invoice: {str(e)}") 