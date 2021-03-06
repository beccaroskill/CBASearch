# CBASearch

## Future to-dos
- Pagination (currently only first 40 results load)
- Search results corpus download
- Topic grouping & filtering 

## Project Journal

### Monday, May 4, 2022
I added functionality for North American Industry Classification System parsing, because this is the format used for industry information in the Department of Labor-sourced data. The coding system kind of reminds me of zip codes or IP addresses, in that there's an encoded hierarchy, so the first $k$ digits denote increasing levels of industry-specificity, with all $n$ digits representing the unique code for the most specific associated industry. Parsing these codes was a little more complex than expected because the coding system is not implemented perfectly (e.g. some classes have several corresponding codes because unique codes could not be assigned to all their subclasses). Next up, I need to make the UI components for sector and topic filtering functional. This should be extremely simple for sector, but I will need to do some offline data parsing to get into topic filtering.
![Preview image 1](/progress_pics/5.04-1.png)

### Monday, April 4, 2022
I updated the search tool (both backend and UI) such that the search term is now designed to be a string the user is hoping to find in the text of the contracts. The results show previews of the 3 lines before and the 3 lines after the line that the string appears in. Here's a preview of where I'm at:
![Preview image 2](/progress_pics/4.03-2.png)
![Preview image 1](/progress_pics/4.03-1.png)

### Friday, April 1, 2022
To get things up and running, I created a pretty simple web app that lets the user search for a contract and view that contract, formatting the lines labeled as section headers as header text. 

I already have access to a database of Canadian CBAs, but I thought it would be cool to add a bunch of agreements from the US too (and in the process, scope out a pipeline for growing the corpus of contracts). I downloaded the metadata for all the contracts available through the Department of Labor's [website](https://olmsapps.dol.gov/olpdr/?&_ga=2.258240718.51574531.1648405057-1819467352.1646754527#CBA%20Search/CBA%20Search/). I then downloaded all the corresponding contracts, which are in PDF format (`data/downloadcontracts.py`). The part I'm struggling with most (because this is actually quite a complex problem) is scanning the PDFs in a manner that preserves the hierarchy in the text, or at least some sense of sections and their respective headers. I made a script (`data/readcontracts.py`) that uses the pdf_to_image and pytesseract libraries to perform OCR that converts the PDFs to TXT. I used a  very rudimentary custom method to detect whether lines are headers, based on the extent to which they are uppercase/sentence case. It doesn't work on all cases, and this process is expensive to run, but I tried it out with 5 contracts as a start.

### Thursday, March 31, 2022
Because I'm not personally familiar with FastAPI, I looked through ChristopherGS's [tutorial](https://christophergs.com/tutorials/ultimate-fastapi-tutorial-pt-6b-linode-deploy-gunicorn-uvicorn-nginx/) to get started. I then found a simple [template app](https://github.com/robmarkcole/simple-fastAPI-webapp) to use as a starting point.
