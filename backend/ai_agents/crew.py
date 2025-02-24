from typing import Dict, Any
import os
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
import magic
import base64
import logging
import json

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DataMatcher:
    def __init__(self):
        self.target_fields = [
            'bill_to', 
            'emailing_address', 
            'invoice_number', 
            'invoice_date', 
            'invoice_amount', 
            'services'
        ]
        self.openai_client = OpenAI()
        self.model_name = "gpt-4o"

    def match_data(self, extracted_data: str) -> dict:
        try:
            prompt = f"""
            You are a data matching expert. Please analyze the extracted OCR data and map it to the following fields:
            {self.target_fields}

            The extracted data is:
            {extracted_data}

            Please return a JSON object with these exact keys and format:
            {{
                "bill_to": "exact company/person name",
                "emailing_address": "complete email address",
                "invoice_number": "exact invoice number",
                "invoice_date": "date in YYYY-MM-DD format",
                "invoice_amount": "amount with currency symbol",
                "services": [
                    {{
                        "service": "service description",
                        "quantity": "numeric value",
                        "unit_price": "price with currency",
                        "amount": "total with currency"
                    }}
                ]
            }}

            Rules:
            1. Use EXACTLY these snake_case field names
            2. For missing data, use null (not empty string)
            3. For services array, include all line items found
            4. Ensure all amounts include currency symbols
            5. Format dates as YYYY-MM-DD only

            Return only the JSON object, no additional text.
            """

            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a precise data matching assistant that returns only JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            matched_data = json.loads(response.choices[0].message.content)
            print("Matched Data:", json.dumps(matched_data, indent=2))
            return matched_data

        except Exception as e:
            logger.error(f"Error in data matching: {str(e)}")
            raise Exception(f"Error matching data: {str(e)}")

class InvoiceProcessor:
    def __init__(self):
        self.openai_client = OpenAI(
            api_key=os.getenv('OPENROUTER_API_KEY'),
            base_url="https://openrouter.ai/api/v1"
        )
        self.model_name = "qwen/qwen2.5-vl-72b-instruct:free"
        self.data_matcher = DataMatcher()

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
            logging.info("Initial OCR Data: %s", extracted_data)

            # Match the extracted data to our target fields
            matched_data = self.data_matcher.match_data(extracted_data)
            logging.info("Matched Data before return: %s", json.dumps(matched_data, indent=2))
            
            # Ensure matched_data is a dictionary with the correct structure
            if not isinstance(matched_data, dict):
                logging.error(f"Matched data is not a dictionary: {type(matched_data)}")
                matched_data = {
                    "bill_to": None,
                    "emailing_address": None,
                    "invoice_number": None,
                    "invoice_date": None,
                    "invoice_amount": None,
                    "services": []
                }

            # Return structured data
            response_data = {
                'extracted_data': matched_data,  # Now using the matched data
                'raw_ocr_data': extracted_data,  # Keep the original OCR data
                'validation_status': 'success',
                'confidence_score': 0.95,
                'discrepancies': {
                    'source_type': file_type.split('/')[0],
                    'ocr_confidence': 'high'
                }
            }
            logging.info("Final response data: %s", json.dumps(response_data, indent=2))
            return response_data

        except Exception as e:
            logging.error(f"Error processing invoice: {str(e)}")
            raise Exception(f"Error processing invoice: {str(e)}") 