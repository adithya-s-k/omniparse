# Quick Start

Install the client:

```bash
pip install omniparse_client
```

Example usage:

```python
from omniparse_client import OmniParse

# Initialize the parser
parser = OmniParse(
    base_url="http://localhost:8000" 
    api_key="op-...", # get the api key from dev.omniparse.com
    verbose=True,
    language="en" )

# Parse a document
document = parser.load_data('path/to/document.pdf')

# Convert to markdown
parser.save_to_markdown(document)
```
