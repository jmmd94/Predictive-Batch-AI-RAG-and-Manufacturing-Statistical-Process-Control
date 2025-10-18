Predictive Batch AI: RAG and Manufacturing Statistical Process Control (MSPC) 🌟

This repository hosts a Proof of Concept (POC) solution demonstrating an intelligent system for monitoring, predicting, and automating responses in complex batch manufacturing environments.



The project uses a relatable "Cake Baking" scenario to showcase the fusion of Advanced Data Science and Generative AI (GenAI) on the Microsoft Azure cloud platform.



Core Objectives:

Anomaly Detection (MSPC): Implement Multivariate Statistical Process Control (MSPC) models (PCA and PLS via Python) to model the "Golden Batch" trajectory and detect subtle deviations in real-time.



Quality Prediction: Utilize PLS regression to forecast final product quality attributes ($\\text{CQA}$s, e.g., Final Height) mid-run, enabling scrap reduction and early intervention.



Intelligent Prescription (RAG): Integrate a Copilot Agent with a Retrieval-Augmented Generation (RAG) system to transform technical model alerts into human-readable, context-aware, and auditable corrective actions.



Project Components:

1\_Data\_Generation: Contains the Python script to create the synthetic, time-series CSV files with programmed faults (Door Open, Under-Mixed Batter).



2\_MSPC\_Modeling: Jupyter Notebooks where the PCA and PLS models are trained on the synthetic CSV data (SIMCA substitute).



3\_GenAI\_Knowledge\_Base: Simulated CSV files and documents (SOPs, CAPA Logs) used by Azure AI Search to ground the RAG component's responses.



4\_Azure\_Deployment: Outlines the architecture for deploying the Python model and orchestrating the Copilot Agent on Azure ML and Azure OpenAI.



Tools Used: Python (Pandas, Scikit-learn), Azure ML, Azure AI Search, and GenAI (LLM).

