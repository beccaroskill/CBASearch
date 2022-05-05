"""Console script for cba_search."""
import argparse
import sys
import uvicorn

def main():
    """Console script for cba_search."""
    # parser = argparse.ArgumentParser()
    # parser.add_argument('_', nargs='*')
    # args = parser.parse_args()

    uvicorn.run("cba_search:app", host="127.0.0.1", port=5000, log_level="info")
    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
