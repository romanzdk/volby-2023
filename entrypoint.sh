#!/usr/bin/env bash
mkdir -p ~/.streamlit/
echo "
[server]
headless = true
port = $PORT
enableCORS = false" > ~/.streamlit/config.toml
streamlit run app/application.py