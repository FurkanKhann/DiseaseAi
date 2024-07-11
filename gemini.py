import google.generativeai as genai
import os


os.environ["API_KEY"] = "AIzaSyAaALLmpDW7wRne7nuHtEbeXOAewlTAk9s"
genai.configure(api_key=os.environ["API_KEY"])

model1 = genai.GenerativeModel('gemini-1.5-flash')
print('gemini model imported')
