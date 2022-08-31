"""Console script for cba_search."""
import sys
import uvicorn

def main():
    """Console script for cba_search."""


    uvicorn.run("cba_search:app", host="127.0.0.1", port=5000, 
                log_level="info", reload=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
