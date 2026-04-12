# Futoshiki Project 2 (CSC14003)

Starter structure for the AI Project 2 assignment:
- Streamlit GUI to load input, solve, and save output
- Input parser based on assignment format
- Forward chaining baseline solver

## Project Structure

```text
Project2/
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── parser.py
│   │   └── types.py
│   ├── solvers/
│   │   └── forward_chaining.py
│   └── utils/
│       └── io.py
│   └── requirements.txt
├── input/
│   └── input-01.txt
├── output/
└── README.md
```

## Run

```bash
pip install -r src/requirements.txt
streamlit run src/main.py
```

## Notes

- This is the initial Streamlit GUI and folder setup.
- Next steps: improve forward chaining, add backward chaining (SLD), A*, comparison solvers, and report assets.
