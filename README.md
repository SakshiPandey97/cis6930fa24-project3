# cis6930fa24project3 : End Pipeline

## Author
**Name:** Sakshi Pandey

## Introduction
This project extends the functionality developed in Project 0. In Project 0, we fetched PDF data from the Norman Police Department (NormanPD) website, parsed incident records, and stored them locally. In this project, we create a web-based interface to:

1. Ingest and parse incident data from either a remote PDF URL or a locally uploaded PDF file.
2. Store the incident data in a local SQLite database.
3. Visualize the data through three different data visualizations, providing insightful summaries of the incidents.

This project represents a later stage of the data pipeline where data is cleaned, processed, and finally presented to end-users with interactive plots.

## **Features and Functionality**

### **1. File and URL Input**
- Users can upload NormanPD-style incident PDFs or provide a URL to a publicly hosted incident report.
- Both the uploaded file and URL input are processed to extract incident data using the `incident_parser` module.

### **2. Visualizations**
This project includes three distinct visualizations:

#### **Visualization 1: Clustering of Records**
- Incidents are clustered based on their nature and location using KMeans clustering and visualized with PCA (Principal Component Analysis).
- This plot helps identify patterns and groups in incident data.
- Hovering over a cluster reveals incident details (e.g., nature and location).

#### **Visualization 2: Bar Graph (Incident Count by Nature)**
- A bar chart compares the count of incidents based on their nature (ex. Assault, Theft).
- Provides an overview of the most and least common incident types.

#### **Visualization 3: Incidents by Hour of the Day**
- A bar chart showing the frequency of incidents during each hour of the day.
- Useful for identifying peak times for incidents.


## **Installation and Setup**

### **Prerequisites**
- Python 3.10 or later
- Pipenv for dependency management

### **Installation Steps**
1. Clone the repository.

2. Install dependencies:
   ```bash
   pipenv install
   ```

3. Activate the virtual environment:
   ```bash
   pipenv shell
   ```

4. Run the application:
   ```bash
   $env:FLASK_APP = "app.py"  
   pipenv run python -m flask run
   ```

5. Access the application at [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## **Usage**

### **Steps to Use the Application**
1. Upload a NormanPD-style PDF or provide a URL to an incident report.
2. Click "Submit" to process the input.
3. Navigate to the Visualizations page to view:
   - Clustering of records
   - Incident count by nature
   - Incidents by hour of the day

---

## **Graph Details**

### **1. Clustering of Records**
- **Purpose:** Group incidents based on their nature and location to identify patterns.
- **Method:**
  - The textual features (nature + location) are vectorized using TF-IDF.
  - KMeans clustering groups similar incidents together.
  - PCA reduces high-dimensional text vectors into two dimensions for visualization.
  - The scatter plot is color-coded by cluster, allowing quick identification of patterns.
- **Visualization:** Scatter plot with clusters differentiated by color.
- **Insights:** Users can hover over data points to view incident details.

### **2. Incident Count by Nature (Bar Graph)**
- **Purpose:** Display the frequency of different types of incidents.
- **Method:**
  - Counts the number of incidents by their nature.
- **Visualization:** Bar chart with bars representing incident counts.
- **Insights:** Highlights the most and least frequent incident types.

### **3. Incidents by Hour of the Day**
- **Purpose:** Show time distribution of incidents.
- **Method:**
  - Extracts and groups incidents by hour from their timestamps.
- **Visualization:** Bar chart with hours on the x-axis and incident counts on the y-axis.
- **Insights:** Useful for identifying peak hours for incidents.

## How to Run the Code

### Prerequisites
- Python 3.12 recommended.
- `pip` for installing dependencies.

### Dependencies
Key dependencies include:
- Flask (for the web interface)
- pandas, numpy, scikit-learn (for data handling and clustering)
- plotly (for interactive visualizations)
- pypdf (for extracting text from PDFs)
- sqlite3 (Python standard library for database)

All dependencies are listed in `Pipfile`.
### Tests
This project includes a minimal set of tests designed to verify the core functionality of the application. The tests use pytest and ensure that the web application behaves as expected for its key features. Below is an overview of the test structure and instructions to run them.

1. test_index_get
Purpose: Verifies that the index page (/) loads successfully.
Expected Outcome: The response status code should be 200, and the content should include the text Upload Incidents.

2. test_index_post_with_url
Purpose: Tests submitting an incident report URL through the index page.
Mocked Functions:
fetchincidents: Simulates fetching a PDF from the provided URL.
extractincidents: Simulates extracting data from the fetched PDF.
populatedb: Simulates populating the SQLite database with the extracted data.
Expected Outcome: The response status code should be 200, and the content should include the text Visualizations.

3. test_visualizations_get
Purpose: Verifies that the visualizations page (/visualizations) loads successfully.
Expected Outcome: The response status code should be 200, and the content should include the text Visualizations.

## **Known Bugs and Assumptions**

### **Known Bugs:**
1. **PDF Parsing Limitations:**
   - Some PDFs with non-standard formatting may fail to parse.
   - Workaround: Ensure the PDF adheres to the NormanPD standard.

2. **Time Parsing Errors:**
   - Incidents without valid timestamps may result in parsing errors.

3. **Clustering Accuracy:**
   - Clustering may group unrelated incidents if the nature/location text is ambiguous.

### **Assumptions:**
1. Input PDFs follow the standard NormanPD incident report format.
2. All timestamps are in the MM/DD/YYYY HH:MM format.
3. The database is recreated on each run for simplicity.

## **Video Demonstration**
A narrated video demonstrating the application can be found here: [YouTube Link](https://youtu.be/Yc0PIYjrZx8)
[![Application Demo](https://img.youtube.com/vi/Yc0PIYjrZx8/0.jpg)](https://youtu.be/Yc0PIYjrZx8)
I've also included the zip file for the video. Due to GitHub's file size limits I couldn't directly upload it.


