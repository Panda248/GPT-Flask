from flask import Flask

app = Flask(__name__)

# test dependencies
try :
    import dotenv
    print("dotenv exists")
except ImportError:
    print("dotenv does not exist")
try :
    import openai
    print("openai exists")
except ImportError:
    print("openai does not exist")
try :
    import langchain
    print("langchain exists")
except ImportError:
    print("langchain does not exist")

from langchain.agents import create_agent
from openai import OpenAI

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from langchain.chat_models import init_chat_model

model = init_chat_model(
    "openai:gpt-4o",
    temperature=0.2,
    timeout=300,
    max_tokens=25000,
)

# Access environment variables
database_url = os.getenv('DATABASE_URL')
secret_key = os.getenv('SECRET_KEY')
debug = os.getenv('DEBUG')

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"