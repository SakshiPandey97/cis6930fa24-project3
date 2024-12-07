import argparse
from project0 import incident_parser 

def main(url):
    incident_data = incident_parser.fetchincidents(url)
    incidents = incident_parser.extractincidents(incident_data)
    
    db = incident_parser.createdb()
    incident_parser.populatedb(db, incidents)
    
    incident_parser.status(db)
    
    db.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, 
                        help="Incident summary url.")
    
    args = parser.parse_args()
    if args.incidents:
        main(args.incidents)