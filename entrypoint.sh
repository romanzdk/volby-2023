#!/usr/bin/env bash
echo """
[server]
headless = true
enableCORS = false""" >> streamlit/config.toml
streamlit run volby_2023/application.py 