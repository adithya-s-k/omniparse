# Installation

### Installation

To install OmniParse, you can use `pip`:

```bash
git clone https://github.com/adithya-s-k/omniparse
cd omniparse
```

Create a Virtual Environment:

```bash
conda create omniparse-venv python=3.10
conda activate omniparse-venv
```

Install Dependencies:

```bash
poetry install
# or
pip install -e .
```

### Usage

Run the Server:

```bash
python server.py --host 0.0.0.0 --port 8000 --documents --media --web
```
