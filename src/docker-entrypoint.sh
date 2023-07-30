#!/bin/bash

python app/indexes.py
python app/seed.py
python app/version.py

uvicorn app.main:app --host 0.0.0.0 --port $PORT
