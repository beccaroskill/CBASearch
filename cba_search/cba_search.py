"""Main module for cba_search."""
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from cba_search.contract_data import ContractDatabase

app = FastAPI(title="CBA Search")
contract_db = ContractDatabase("data/DOL_Scrape/ContractText_Reflattened", 
                               "data/CBAList.csv",
                               "data/2022_NAICS_Structure.csv")
templates = Jinja2Templates(directory="templates/")
app.mount("/static", StaticFiles(directory="static"), name="static")

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
            <h1>Navigate to <a href="/search">/search</a></h1>
        </body>
    </html>
    """

@app.get("/search")
def form_post(request: Request):
    search_results = contract_db.get_all_contracts()
    return templates.TemplateResponse(
        "search.html", context=get_context(request, search_results)
    )

@app.post("/search")
def form_post(request: Request, 
              search_term: str = Form("search_term"), 
              industry_codes: str = Form("industry_codes")):
    search_filters = {"industry_codes": industry_codes}
    if search_term != "search_term":
        search_results = contract_db.get_search_results(search_term, search_filters)
    else:
        search_results = contract_db.get_all_contracts(search_filters)
    return templates.TemplateResponse(
        "search.html", context=get_context(request, search_results)
    )

@app.get("/contracts/{contract_id}")
async def read_item(request: Request, contract_id: int):
    contract = contract_db.get_contract_text(contract_id)
    return templates.TemplateResponse(
        "contract.html", context={"request": request, 
                                  "contract": contract}
    )