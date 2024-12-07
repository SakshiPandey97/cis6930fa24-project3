import os
import sqlite3
import re
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash
import logging
from werkzeug.utils import secure_filename
from src.project0.incident_parser import fetchincidents, extractincidents, createdb, populatedb
import plotly.graph_objects as go
import plotly
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Server Error: {error}")
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"Page Not Found: {error}")
    return render_template('404.html'), 404

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB_PATH = os.path.join(os.path.dirname(__file__), 'resources', 'normanpd.db')
if not os.path.exists(os.path.join(os.path.dirname(__file__), 'resources')):
    os.makedirs(os.path.join(os.path.dirname(__file__), 'resources'))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
"""
def get_db_connection():
    conn = sqlite3.connect(app.config['DB_PATH'])
    conn.row_factory = sqlite3.Row
    return conn
"""
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        incident_url = request.form.get("incident_url")
    
        file = request.files.get("incident_file")
        conn = createdb()  
        if incident_url and incident_url.strip():
            pdf_data = fetchincidents(incident_url)
            if pdf_data:
                incidents = extractincidents(pdf_data)
                populatedb(conn, incidents)
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'rb') as f:
                pdf_data = f.read()
            incidents = extractincidents(pdf_data)
            populatedb(conn, incidents)
        
        conn.close()
        return redirect(url_for('visualizations'))

    return render_template('index.html')

@app.route('/visualizations')
def visualizations():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM incidents", conn)
    conn.close()

    if df.empty:
        return render_template('visualizations.html', 
                               cluster_plot="", 
                               bar_plot="", 
                               time_plot="", 
                               time_bins_plot="",
                               message="No data available. Please upload a file or enter a URL.")

    df['nature'] = df['nature'].fillna('Unknown')
    df['incident_location'] = df['incident_location'].fillna('Unknown')
    
    def parse_datetime(s):
        pattern = r"(\d{1,2}/\d{1,2}/\d{4})\s+(\d{1,2}:\d{2})?"
        match = re.match(pattern, str(s))
        if match:
            date_str = match.group(1)
            time_str = match.group(2) if match.group(2) else "00:00"
            dt_str = f"{date_str} {time_str}"
            return datetime.strptime(dt_str, "%m/%d/%Y %H:%M")
        return None

    df['datetime'] = df['incident_time'].apply(parse_datetime)
    df['date_only'] = df['datetime'].dt.date

    #graph 1
    texts = (df['nature'] + " " + df['incident_location']).values
    vectorizer = TfidfVectorizer(stop_words='english')
    X = vectorizer.fit_transform(texts)

    kmeans = KMeans(n_clusters=3, random_state=42, n_init='auto')
    labels = kmeans.fit_predict(X)

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(X.toarray())

    cluster_fig = go.Figure()
    cluster_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#E0F7FA", 
        plot_bgcolor="#E0F7FA",
        title="Incident Clustering by Nature and Location",
        xaxis_title="PCA Dimension 1",
        yaxis_title="PCA Dimension 2",
        showlegend=True,
        font=dict(family="Arial, sans-serif")
    )

    cluster_colors = ["#FFD1DC", "#E6E6FA", "#FFFACD"]

    unique_labels = np.unique(labels)
    for i, cluster_id in enumerate(unique_labels):
        cluster_points = coords[labels == cluster_id]
        subset = df[labels == cluster_id]
        cluster_fig.add_trace(go.Scatter(
            x=cluster_points[:,0],
            y=cluster_points[:,1],
            mode='markers',
            name=f"Cluster {cluster_id}",
            text=[f"Nature: {n}<br>Location: {loc}" for n, loc in zip(subset['nature'], subset['incident_location'])],
            hoverinfo='text',
            marker=dict(size=8, line=dict(width=1, color='darkgrey'), color=cluster_colors[i % len(cluster_colors)])
        ))
    cluster_plot = json.dumps(cluster_fig, cls=plotly.utils.PlotlyJSONEncoder)

    #graph 2
    nature_counts = df['nature'].value_counts().sort_values(ascending=False)
    bar_fig = go.Figure([go.Bar(
        x=nature_counts.index, 
        y=nature_counts.values,
        text=nature_counts.values,
        textposition='auto',
        marker_color="#D8BFD8"  #lavender haze
    )])
    bar_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFE4E1",  
        plot_bgcolor="#FFE4E1",
        title="Count of Incidents by Nature",
        xaxis_title="Nature of Incident",
        yaxis_title="Count of Incidents",
        margin=dict(l=40, r=40, t=40, b=100),
        font=dict(family="Arial, sans-serif")
    )
    bar_fig.update_xaxes(tickangle=45)
    bar_plot = json.dumps(bar_fig, cls=plotly.utils.PlotlyJSONEncoder)

    #graph 3
    loc_counts = df['incident_location'].value_counts().head(10)
    loc_fig = go.Figure([go.Bar(
        x=loc_counts.index,
        y=loc_counts.values,
        text=loc_counts.values,
        textposition='auto',
        marker_color="#ADD8E6" 
    )])
    loc_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#E6E6FA", 
        plot_bgcolor="#E6E6FA",
        title="Top 10 Locations by Incident Count",
        xaxis_title="Location",
        yaxis_title="Count of Incidents",
        margin=dict(l=40, r=40, t=40, b=100),
        font=dict(family="Arial, sans-serif")
    )
    loc_fig.update_xaxes(tickangle=45)
    time_plot = json.dumps(loc_fig, cls=plotly.utils.PlotlyJSONEncoder)

    
    df['hour'] = df['datetime'].dt.hour
    hour_counts = df['hour'].value_counts().sort_index()
    time_bins_fig = go.Figure([go.Bar(
        x=hour_counts.index,
        y=hour_counts.values,
        text=hour_counts.values,
        textposition='auto',
        marker_color="#FFD1DC"
    )])
    time_bins_fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#FFFACD",
        plot_bgcolor="#FFFACD",
        title="Incidents by Hour of the Day",
        xaxis_title="Hour of Day (0-23)",
        yaxis_title="Number of Incidents",
        margin=dict(l=40, r=40, t=40, b=40),
        font=dict(family="Arial, sans-serif")
    )
    time_bins_plot = json.dumps(time_bins_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('visualizations.html',
                           cluster_plot=cluster_plot,
                           bar_plot=bar_plot,
                           time_plot=time_plot,
                           time_bins_plot=time_bins_plot,
                           message="")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
