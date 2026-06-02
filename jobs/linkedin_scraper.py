import streamlit as st
import requests
import os
import pandas as pd

JSEARCH_API_KEY = os.getenv("JSEARCH_API_KEY")

def fetch_jobs(job_title, job_location, job_count):
    """Fetch jobs from JSearch API"""
    url = "https://jsearch.p.rapidapi.com/search"
    
    query = f"{job_title} in {job_location}"
    
    headers = {
        "X-RapidAPI-Key": JSEARCH_API_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    params = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "country": "in"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        jobs = []
        for job in data.get("data", [])[:job_count]:
            jobs.append({
                "Job Title": job.get("job_title", "N/A"),
                "Company Name": job.get("employer_name", "N/A"),
                "Location": job.get("job_city", "N/A") + ", " + job.get("job_country", ""),
                "Job Type": job.get("job_employment_type", "N/A"),
                "Website URL": job.get("job_apply_link", "#"),
                "Job Description": job.get("job_description", "N/A")[:500] + "..."
            })
        
        return pd.DataFrame(jobs)
    
    except Exception as e:
        st.error(f"Error fetching jobs: {str(e)}")
        return pd.DataFrame()


def render_linkedin_scraper():
    """Render job search UI using JSearch API"""
    
    st.markdown("""
        <style>
        .job-form {
            background: rgba(10, 102, 194, 0.05);
            border-radius: 10px;
            padding: 20px;
            border-left: 4px solid #0A66C2;
            margin-bottom: 20px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="job-form">', unsafe_allow_html=True)
    st.markdown("### 💼 LinkedIn Job Search")
    st.markdown("Find real-time job listings from LinkedIn and top job sites")
    
    col1, col2, col3 = st.columns([0.5, 0.3, 0.2])
    
    with col1:
        job_title = st.text_input(
            "Job Title",
            placeholder="e.g. Data Scientist, Software Engineer"
        )
    
    with col2:
        job_location = st.text_input(
            "Location",
            value="India",
            placeholder="e.g. Bangalore, Mumbai"
        )
    
    with col3:
        job_count = st.number_input(
            "Number of Jobs",
            min_value=1,
            max_value=10,
            value=3,
            step=1
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("Search Jobs", type="primary", use_container_width=True):
        if not job_title:
            st.warning("Please enter a job title!")
            return
        
        with st.spinner("Searching jobs..."):
            df = fetch_jobs(job_title, job_location, job_count)
        
        if df.empty:
            st.warning("No jobs found. Try different search terms.")
            return
        
        st.success(f"Found {len(df)} jobs!")
        
        for i, row in df.iterrows():
            with st.expander(f"💼 {row['Job Title']} at {row['Company Name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"📍 **Location:** {row['Location']}")
                    st.write(f"💼 **Type:** {row['Job Type']}")
                with col2:
                    st.markdown(f"[Apply Now →]({row['Website URL']})")
                
                st.write("**Description:**")
                st.write(row['Job Description'])