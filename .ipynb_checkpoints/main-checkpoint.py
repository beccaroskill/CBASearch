"""
https://fastapi.tiangolo.com/advanced/custom-response/#html-response
"""

from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from loaddata import get_contract_lines

app = FastAPI(title="CBA Search")
app.mount("/static", StaticFiles(directory="static"), name="static")
print('woot', app)
templates = Jinja2Templates(directory="templates/")

@app.get("/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Simple HTML app</title>
        </head>
        <body>
            <h1>Navigate to <a href="http://localhost:8000/form">/form</a></h1>
        </body>
    </html>
    """


@app.get("/form")
def form_post(request: Request):
    contract_id = "Enter a contract id"
    return templates.TemplateResponse(
        "form.html", context={"request": request, "results": contract_id}
    )


@app.post("/form")
def form_post(request: Request, contract_id: str = Form(...)):
    contract_text = get_contract_lines(contract_id)
    return templates.TemplateResponse(
        "form.html", context={"request": request, "results": contract_text, "contract_id": contract_id}
    )
