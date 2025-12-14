from dotenv import load_dotenv
import os

load_dotenv()

AI_TOKEN   		= os.getenv("AI_TOKEN")
BOT_TOKEN  		= os.getenv('BOT_TOKEN')
ADMIN_ID   		= int(os.getenv('ADMIN_ID'))
DB_NAME    		= os.getenv('DB_NAME')
SYSTEM_PROMPT   = os.getenv('SYSTEM_PROMPT')