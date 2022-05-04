"""
https://fastapi.tiangolo.com/advanced/custom-response/#html-response
"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from contractdata import ContractDatabase

app = FastAPI(title="CBA Search")
app.mount("/static", StaticFiles(directory="static"), name="static")
contract_db = ContractDatabase("data/DOL_Scrape/ContractText", 
                               "data/CBAList.csv",
                               "data/2022_NAICS_Structure.csv")
templates = Jinja2Templates(directory="templates/")

def get_context(request, search_results):
    return {"request": request, 
            "industries": contract_db.get_industries(),
            "topics": ['All topics',
                       'Unit definition',
                       'Compensation',
                       'Healthcare',
                       'Leaves & Absences'],
            "sectors": ['All sectors (Public/Private)',
                        'Private',
                        'Public'],
            "results": search_results}

@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Collective Bargaining Agreement Search Tool</title>
        </head>
        <body>
            <h1>Navigate to <a href="http://localhost:8000/search">/search</a></h1>
        </body>
    </html>
    """

@app.get("/search")
def form_post(request: Request):
    search_results = []
    return templates.TemplateResponse(
        "search.html", context=get_context(request, search_results)
    )

@app.post("/search")
def form_post(request: Request, search_term: str = Form(...), industry_codes: str = Form(...)):
    search_filters = {"industry_codes": industry_codes}
    search_results = contract_db.get_search_results(search_term, search_filters)
    return templates.TemplateResponse(
        "search.html", context=get_context(request, search_results)
    )
