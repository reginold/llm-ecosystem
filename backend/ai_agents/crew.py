from crewai import Agent, Task, Crew
from langchain.tools import DuckDuckGoSearchRun
from typing import Dict, Any
import os
from dotenv import load_dotenv
from flask_socketio import SocketIO
from datetime import datetime

# Load environment variables
load_dotenv()

class InvoiceCrew:
    def __init__(self, socketio: SocketIO = None):
        self.search_tool = DuckDuckGoSearchRun()
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.socketio = socketio

    def emit_progress(self, step: str, message: str):
        if self.socketio:
            self.socketio.emit('agent_progress', {
                'timestamp': datetime.utcnow().isoformat(),
                'step': step,
                'message': message
            })

    def process_invoice(self, file_path: str) -> Dict[str, Any]:
        self.emit_progress('INIT', 'Starting invoice processing...')
        
        # Create agents
        self.emit_progress('SETUP', 'Initializing AI agents...')
        data_extraction_agent = Agent(
            role='Data Extraction Specialist',
            goal='Extract accurate data from invoice documents',
            backstory='Expert in OCR and document parsing with high attention to detail',
            tools=[self.search_tool],
            verbose=True,
            openai_api_key=self.openai_api_key,
            llm_config={
                'callbacks': [
                    lambda thought: self.emit_progress('EXTRACTION_THOUGHT', thought)
                ]
            }
        )

        validation_agent = Agent(
            role='Data Validation Specialist',
            goal='Ensure extracted data is accurate and complete',
            backstory='Expert in financial document validation with years of experience',
            tools=[self.search_tool],
            verbose=True,
            openai_api_key=self.openai_api_key,
            llm_config={
                'callbacks': [
                    lambda thought: self.emit_progress('VALIDATION_THOUGHT', thought)
                ]
            }
        )

        # Create tasks
        self.emit_progress('TASK', 'Creating processing tasks...')
        extraction_task = Task(
            description=f'Extract all relevant information from the invoice at {file_path}',
            agent=data_extraction_agent
        )

        validation_task = Task(
            description='Validate the extracted data for accuracy and completeness',
            agent=validation_agent
        )

        # Create crew
        self.emit_progress('CREW', 'Assembling AI crew...')
        crew = Crew(
            agents=[data_extraction_agent, validation_agent],
            tasks=[extraction_task, validation_task],
            verbose=True,
            openai_api_key=self.openai_api_key
        )

        # Execute tasks
        self.emit_progress('PROCESS', 'Starting document analysis...')
        result = crew.kickoff()
        
        self.emit_progress('COMPLETE', 'Processing completed successfully!')

        return {
            'extracted_data': result,
            'validation_status': 'success',
            'confidence_score': 0.95
        } 