# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import requests
# import os

# app = FastAPI()

# # Print the API key for debugging purposes
# api_key = os.getenv('OPENAI_API_KEY')
# print("OpenAI API Key:", api_key)

# # Load your OpenAI API key from environment variables or raise an error if not found
# OPENAI_API_KEY = api_key
# if not OPENAI_API_KEY:
#     raise RuntimeError("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")

# OPENAI_API_URL = "https://api.openai.com/v1/engines/davinci-codex/completions"

# class ProjectData(BaseModel):
#     description: str

# class RiskAssessment(BaseModel):
#     risks: list
#     assessment: str

# def call_openai_api(prompt: str):
#     headers = {
#         "Authorization": f"Bearer {OPENAI_API_KEY}",
#         "Content-Type": "application/json",
#     }
#     data = {
#         "prompt": prompt,
#         "max_tokens": 150,
#         "n": 1,
#         "stop": None,
#         "temperature": 0.5,
#     }
#     response = requests.post(OPENAI_API_URL, headers=headers, json=data)
#     if response.status_code != 200:
#         raise HTTPException(status_code=response.status_code, detail="Error calling OpenAI API")
#     return response.json()['choices'][0]['text'].strip()

# @app.post("/identify_risks/", response_model=RiskAssessment)
# def identify_risks(project: ProjectData):
#     prompt = f"Identify potential risks in the following project description:\n\n{project.description}\n\nRisks:"
#     risks = call_openai_api(prompt)
#     prompt_assessment = f"Assess the likelihood and impact of the following risks:\n\n{risks}\n\nAssessment:"
#     assessment = call_openai_api(prompt_assessment)
#     return RiskAssessment(risks=risks.split('\n'), assessment=assessment)

# @app.get("/")
# def read_root():
#     return {"message": "Agile Risk Management API"}
