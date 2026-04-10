# Orphanage Care

A web application to manage an orphanage's medical records and children details, featuring automatic reminders.

## Run on Any Device

The project has been configured to use a local **SQLite database**, which means you do **not** need to install MySQL, configure a server, or fix any database credentials. The required database file (`medicine.db`) is automatically generated the very first time you run the app—making it extremely easy to run when downloading as a ZIP or cloning via Git.

### Setup Instructions:

1. Clone the repository (or download and extract the ZIP):
   ```bash
   git clone https://github.com/srushtibugdalwar/orphanage-care.git
   cd orphanage-care
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and go to `http://127.0.0.1:5000`
