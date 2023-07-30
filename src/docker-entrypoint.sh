#!/bin/bash

python indexes.py
python seed.py
python version.py

uvicorn app.main:app --host 0.0.0.0 --port $PORT
