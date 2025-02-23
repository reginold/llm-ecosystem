from typing import Dict, Any
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO
from datetime import datetime
from openai import OpenAI
import PyPDF2
import magic  # python-magic library for file type detection
from PIL import Image
import pytesseract

# Load environment variables
load_dotenv()

class InvoiceProcessor:
    def __init__(self, socketio: SocketIO = None):
        self.openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.socketio = socketio
        self.model_name = os.getenv('OPENAI_MODEL_NAME', 'gpt-4o')

    def emit_progress(self, step: str, message: str):
        if self.socketio:
            self.socketio.emit('agent_progress', {
                'timestamp': datetime.utcnow().isoformat(),
                'step': step,
                'message': message
            })

    def read_file_content(self, file_path: str) -> str:
        """Read file content based on file type"""
        # Detect file type
        file_type = magic.from_file(file_path, mime=True)
        
        try:
            if file_type == 'application/pdf':
                # Handle PDF files
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ''
                    for page in pdf_reader.pages:
                        text += page.extract_text() + '\n'
                    return text
            
            elif file_type.startswith('image/'):
                # Process images with OCR
                try:
                    image = Image.open(file_path)
                    # Convert image to text using OCR
                    text = pytesseract.image_to_string(image)
                    if not text.strip():
                        return f"Warning: No text could be extracted from image: {file_path}"
                    return text
                except Exception as e:
                    raise Exception(f"Error processing image with OCR: {str(e)}")
            
            elif file_type.startswith('text/'):
                # Handle text files with proper encoding detection
                with open(file_path, 'rb') as file:
                    # Read as bytes first
                    raw_content = file.read()
                    # Try different encodings
                    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    for encoding in encodings:
                        try:
                            return raw_content.decode(encoding)
                        except UnicodeDecodeError:
                            continue
                    raise ValueError(f"Could not decode file with any of the attempted encodings: {encodings}")
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        self.emit_progress('INIT', 'Starting invoice processing...')
        
        try:
            # Get file type first
            file_type = magic.from_file(file_path, mime=True)
            
            # Read the file content with proper handling
            invoice_content = self.read_file_content(file_path)

            # Process with OpenAI
            self.emit_progress('PROCESS', 'Analyzing invoice content...')
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert invoice analyzer. Extract all relevant information from the invoice including dates, amounts, item details, and vendor information. Format the output as JSON with keys: invoice_number, date, vendor, items (array), total_amount, currency."},
                    {"role": "user", "content": f"Please analyze this invoice and extract all relevant information: {invoice_content}"}
                ],
                temperature=0.1
            )

            # Extract the response
            extracted_data = response.choices[0].message.content
            
            self.emit_progress('COMPLETE', 'Processing completed successfully!')

            return {
                'extracted_data': extracted_data,
                'validation_status': 'success',
                'confidence_score': 0.95,
                'discrepancies': {
                    'source_type': file_type.split('/')[0],  # 'image' or 'application' or 'text'
                    'ocr_confidence': 'high' if len(invoice_content) > 100 else 'low',
                    'extracted_text': invoice_content[:200] + '...' if len(invoice_content) > 200 else invoice_content,
                    'analysis_result': extracted_data
                }
            }

        except Exception as e:
            self.emit_progress('ERROR', f'Error processing invoice: {str(e)}')
            raise e 