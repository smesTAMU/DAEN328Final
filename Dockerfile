FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install PostgreSQL client (optional for debugging)
RUN apt-get update && apt-get install -y postgresql-client && apt-get clean

# Copy entire project
COPY . .

# Avoid && in CMD, use ; so Streamlit runs even if main.py is slow or exits with warning
CMD ["bash", "-c", "python main.py; streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]

