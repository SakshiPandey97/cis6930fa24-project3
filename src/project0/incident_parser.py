import urllib.request
from urllib.error import HTTPError
from pypdf import PdfReader
import re
import os
import sqlite3

def fetchincidents(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    }
    request = urllib.request.Request(url, headers=headers)

    try:
        response = urllib.request.urlopen(request)
        data = response.read()
        return data
    except HTTPError as e:
        print(f"HTTP Error: {e.code} - {e.reason}")
        return None

def extractincidents(pdf_data):
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    pdf_file_path = 'tmp/downloaded_file.pdf'
    with open(pdf_file_path, 'wb') as f:
        f.write(pdf_data)

    with open(pdf_file_path, 'rb') as f:
        reader = PdfReader(f)

        incidents = []
        line_count = 0
        current_incident = None
        skipped_lines = []
        
        date_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}(\s+\d{1,2}:\d{2})?$")

        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text = page.extract_text(extraction_mode="layout")
            
            if text is None:
                continue

            lines = text.split('\n')

            for line in lines:
                line = line.strip()
                line_count += 1
                #ignore the title
                if line == "NORMAN POLICE DEPARTMENT" or line == "Daily Incident Summary (Public)":
                    skipped_lines.append(line)
                    continue
                #ignore the headers
                if all(keyword in line for keyword in ["Date / Time", "Incident Number", "Location", "Nature", "Incident ORI"]):
                    skipped_lines.append(line)
                    continue

                
                if line == "" or date_pattern.match(line):
                    skipped_lines.append(line)
                    continue

                parts = re.split(r'\s{2,}', line)
                #assumption for multi-line locations.
                if len(parts) < 5:
                    if current_incident and not date_pattern.match(line):
                        current_incident['Location'] += " " + line
                    else:
                        skipped_lines.append(line)
                    continue

                date_time = parts[0]
                incident_number = parts[1]
                location = parts[2]
                nature = parts[3]
                ori = parts[4]

                current_incident = {
                    'Date/Time': date_time,
                    'Incident Number': incident_number,
                    'Location': location,
                    'Nature': nature,
                    'Incident ORI': ori
                }

                incidents.append(current_incident)

        #print(f"Total: {len(incidents)}")
        #print("Skipped lines:", skipped_lines)
        return incidents




def createdb():
    home_db = "resources"
    db_path = os.path.join(home_db, "normanpd.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    if not os.path.exists(home_db):
        os.makedirs(home_db)
    db_path = 'resources/normanpd.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS incidents 
    (incident_time TEXT,incident_number TEXT,incident_location TEXT,nature TEXT,incident_ori TEXT);''')
    conn.commit()
    return conn

def populatedb(db, incidents):
    #print(incidents)
    cursor = db.cursor()
    
    for incident in incidents:
        cursor.execute('''INSERT INTO incidents(incident_time, incident_number, incident_location, nature, incident_ori)
            VALUES (?, ?, ?, ?, ?)
        ''', (incident.get('Date/Time'), 
              incident.get('Incident Number'), 
              incident.get('Location'), 
              incident.get('Nature'), 
              incident.get('Incident ORI')))
    
    db.commit()

def status(db):
    cursor = db.cursor()
    cursor.execute('''
        SELECT nature, COUNT(*)
        FROM incidents
        WHERE nature IS NOT NULL AND nature != ''
        GROUP BY nature
        ORDER BY nature COLLATE BINARY ASC;
    ''')
    #collate uses the unicode values to sort. so case-sensitive, the uppercase will come first.
    rows = cursor.fetchall()

    for row in rows:
        nature, count = row
        print(f"{nature}|{count}")