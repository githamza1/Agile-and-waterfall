from fastapi import FastAPI, HTTPException, Request
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
import logging
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List

app = FastAPI()

# Loading environment variables from storekey.env file
load_dotenv(dotenv_path='storekey.env')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

logging.basicConfig(level=logging.DEBUG)

templates = Jinja2Templates(directory="templates")

class ProjectData(BaseModel):
    description: str

class RiskAnalysisData(BaseModel):
    descriptions: List[str]
    human_risks: List[List[str]]

def call_openai_api(prompt: str):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.5,
    }
    response = requests.post(OPENAI_API_URL, headers=headers, json=data)
    logging.debug(f"Response Status Code: {response.status_code}")
    logging.debug(f"Response Text: {response.text}")
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Error calling OpenAI API")
    return response.json()['choices'][0]['message']['content'].strip()

@app.post("/identify_risks/")
def identify_risks(project: ProjectData):
    prompt = f"Identify potential risks in the following project description:\n\n{project.description}\n\nRisks:"
    risks = call_openai_api(prompt)
    prompt_assessment = f"Assess the likelihood and impact of the following risks:\n\n{risks}\n\nAssessment:"
    assessment = call_openai_api(prompt_assessment)
    return {"risks": risks.split('\n'), "assessment": assessment}

@app.post("/mitigate_risks/")
def mitigate_risks(project: ProjectData):
    prompt = f"Provide the ways through which the Risks can be avoided according to the agile project management:\n\n{project.description}\n\nRisk Mitigation:"
    mitigation = call_openai_api(prompt)
    return {"mitigation": mitigation}

@app.post("/clean_description/")
def clean_description(project: ProjectData):
    prompt = f"Clean the following project description by removing unnecessary information and ensuring clarity:\n\n{project.description}\n\nCleaned Description:"
    cleaned_description = call_openai_api(prompt)
    return {"cleaned_description": cleaned_description}

@app.post("/analyze_risks/")
async def analyze_risks(request: Request):
    try:
        # Extract the data from the request
        data = await request.json()
        descriptions = data.get('project_descriptions', [])
        human_risks = data.get('human_risks', [])

        # Ensure both lists have the same length
        if len(descriptions) != len(human_risks):
            raise ValueError("Mismatch between number of descriptions and number of risk lists")

        # Process each description and corresponding human risks
        results = []
        for desc, risks in zip(descriptions, human_risks):
            # Perform risk analysis
            predicted_risks = await call_openai_api(f"Identify potential risks in the following project description:\n\n{desc}\n\nRisks:")
            results.append({
                "description": desc,
                "human_risks": risks,
                "predicted_risks": predicted_risks
            })

        return {"results": results}

    except ValueError as ve:
        logging.error(f"ValueError occurred: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logging.error(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the request")
    

@app.post("/generate_productivity/")
async def generate_productivity(project: ProjectData):
    prompt = f"""
    Read the following project description and determine 5 float productivity values for Agile and 5 float productivity values for Waterfall which indicate their productivity at 5 different time points during the development duration of the given project.

    Format the response as follows:
    Agile:
    value1
    value2
    value3
    value4
    value5

    Waterfall:
    value1
    value2
    value3
    value4
    value5
    """
    
    try:
        response = call_openai_api(prompt)
        
        # Parse the response
        lines = response.split('\n')
        agile_productivity = []
        waterfall_productivity = []
        current_section = None
        
        for line in lines:
            if line.startswith('Agile:'):
                current_section = 'Agile'
            elif line.startswith('Waterfall:'):
                current_section = 'Waterfall'
            elif current_section == 'Agile' and line.strip():
                agile_productivity.append(line.strip())
            elif current_section == 'Waterfall' and line.strip():
                waterfall_productivity.append(line.strip())
        
        return {
            "agile_productivity": agile_productivity,
            "waterfall_productivity": waterfall_productivity
        }
    
    except Exception as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/generate_performance/")
async def generate_performance(project: ProjectData):
    prompt = f"""
    Read the following project description and determine 5 float-data-type performance values for Agile and 5 float-datatype performance values for Waterfall which indicate their performance at 5 different time points during the development duration of the given project.

    Format the response as follows:
    Agile:
    value1
    value2
    value3
    value4
    value5

    Waterfall:
    value1
    value2
    value3
    value4
    value5
    """
    
    try:
        response = call_openai_api(prompt)
        
        # Parse the response
        lines = response.split('\n')
        agile_performance = []
        waterfall_performance = []
        current_section = None
        
        for line in lines:
            if line.startswith('Agile:'):
                current_section = 'Agile'
            elif line.startswith('Waterfall:'):
                current_section = 'Waterfall'
            elif current_section == 'Agile' and line.strip():
                agile_performance.append(line.strip())
            elif current_section == 'Waterfall' and line.strip():
                waterfall_performance.append(line.strip())
        
        return {
            "agile_performance": agile_performance,
            "waterfall_performance": waterfall_performance
        }
    
    except Exception as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/generate_mitigation/")
async def generate_mitigation(project: ProjectData):
    prompt = f"""
    Read the following project description and determine 5 float-datatype Risk mitigation values for Agile and 5 float-datatype risk mitigation values for Waterfall which indicate their ability to mitigate risks at 5 different time points during the development duration of the given project.

    Format the response as follows:
    Agile:
    value1
    value2
    value3
    value4
    value5

    Waterfall:
    value1
    value2
    value3
    value4
    value5
    """
    
    try:
        response = call_openai_api(prompt)
        
        # Parse the response
        lines = response.split('\n')
        agile_mitigation = []
        waterfall_mitigation = []
        current_section = None
        
        for line in lines:
            if line.startswith('Agile:'):
                current_section = 'Agile'
            elif line.startswith('Waterfall:'):
                current_section = 'Waterfall'
            elif current_section == 'Agile' and line.strip():
                agile_mitigation.append(line.strip())
            elif current_section == 'Waterfall' and line.strip():
                waterfall_mitigation.append(line.strip())
        
        return {
            "agile_mitigation": agile_mitigation,
            "waterfall_mitigation": waterfall_mitigation
        }
    
    except Exception as e:
        # Handle any errors that occur
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/design_page", response_class=HTMLResponse)
async def serve_design_page(request: Request):
    return templates.TemplateResponse("design.html", {"request": request, "stage": "", "content": ""})

@app.post("/generate_design/") ############################
async def generate_design(project: ProjectData):
    prompt = f"Generate a detailed plan of the design stage for the given project description if we implement agile project and compare it with Waterfall model:\n\n{project.description}\n\nDesign: "
    design_content = call_openai_api(prompt)
    return {"stage": "Design", "content": design_content}

@app.get("/prototyping", response_class=HTMLResponse)
async def get_prototyping(request: Request, description: Optional[str] = Query(None)):
    if description is None:
        return {"detail": "Description parameter is required"}
    
    prompt = f"Generate a detailed plan for the prototyping stage of an agile project for the given project description and compare it with prototyping in Waterfall model if there is any.\n\n{description}\n\nPrototyping:"
    prototyping_content = call_openai_api(prompt)
    return templates.TemplateResponse("prototyping.html", {"request": request, "stage": "Prototyping", "content": prototyping_content})


from fastapi import Request, Query

@app.get("/customer_evaluation", response_class=HTMLResponse)
async def get_customer_evaluation(request: Request, description: str = Query(...)):
    prompt = f"Generate a detailed plan for the customer evaluation stage of an agile project for the given project description and compare it with the evaluation phase in the Waterfall model, if any.\n\n{description}\n\nCustomer Evaluation:"
    response = call_openai_api(prompt)
    customer_evaluation_content = response.get("content", "") if isinstance(response, dict) else response
    return templates.TemplateResponse("customer_evaluation.html", {"request": request, "stage": "Customer Evaluation", "content": customer_evaluation_content})

@app.get("/review_and_update", response_class=HTMLResponse)
async def get_review_and_update(request: Request, description: str = Query(..., description="Project description")):
    prompt = f"Generate a detailed plan for the review and update stage of an agile project for the given project description and compare it with the update stage in the Waterfall model, if any.\n\n{description}\n\nReview and Update:"
    review_and_update_content = call_openai_api(prompt)
    return templates.TemplateResponse("review_and_update.html", {"request": request, "stage": "Review and Update", "content": review_and_update_content})

@app.get("/development", response_class=HTMLResponse)
async def get_development(request: Request, description: str = Query(..., description="Project description")):
    prompt = f"Generate a detailed plan for the development stage of an agile project for the given project description and compare it with development in the Waterfall model.\n\n{description}\n\nDevelopment:"
    development_content = call_openai_api(prompt)
    return templates.TemplateResponse("development.html", {"request": request, "stage": "Development", "content": development_content})

@app.get("/testing", response_class=HTMLResponse)
async def get_testing(request: Request, description: str = Query(..., description="Project description")):
    prompt = f"Generate a detailed plan for the testing stage of an agile project afor the given project descriptionnd compare it with testing in the Waterfall model.\n\n{description}\n\nTesting:"
    testing_content = call_openai_api(prompt)
    return templates.TemplateResponse("testing.html", {"request": request, "stage": "Testing", "content": testing_content})

@app.get("/maintenance", response_class=HTMLResponse)
async def get_maintenance(request: Request, description: str = Query(..., description="Project description")):
    prompt = f"Generate a detailed plan for the maintenance stage of an agile project for the given project description and compare it with maintenance in the Waterfall model.\n\n{description}\n\nMaintenance:"
    maintenance_content = call_openai_api(prompt)
    return templates.TemplateResponse("maintenance.html", {"request": request, "stage": "Maintenance", "content": maintenance_content})


@app.get("/recommendation")
def get_recommendation(description: Optional[str] = None):
    if description:
        prompt = f"Based on the following project description, recommend whether Agile or Waterfall is more suitable:\n\n{description}"
        recommendation_content = call_openai_api(prompt)
    else:
        recommendation_content = "No description provided."

    return JSONResponse(content={"recommendation": recommendation_content})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

