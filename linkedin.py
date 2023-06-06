from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
import pandas as pd

def clean_no_of_jobs(jobs):
    jobs = re.sub('[^0-9]', '', jobs)
    return int(jobs)

url = 'https://www.linkedin.com/jobs/search/?keywords=Fachinformatiker%20Anwendungsentwicklung&location=Hamburg%2C%20Hamburg%2C%20Germany&locationId=&geoId=106430557&f_TPR=&f_PP=106430557&distance=75&f_JT=F&f_E=2&position=1&pageNum=0'
wd = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
wd.get(url)

no_of_jobs = clean_no_of_jobs(wd.find_element(By.CLASS_NAME, 'results-context-header__job-count').get_attribute('innerText'))

if (no_of_jobs > 500):
    no_of_jobs = 250

#scroll as far as possible
i = 2
while i <= int(no_of_jobs/25)+1:
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    i += 1
    try:
        wd.find_element_by_xpath('/html/body/main/div/section/button').click()
        time.sleep(4)
    except:
        pass
        time.sleep(4)


#list jobs
job_lists = wd.find_elements(By.CLASS_NAME, 'jobs-search__results-list')
for job_list in job_lists:
    jobs = job_list.find_elements(By.TAG_NAME, 'li')

#data arrays
job_title = []
company_name = []
location = []
date = []
job_link = []
jd = []
seniority = []
emp_type = []
job_func = []
industries = []

chunk_size = 10
job_counter = 0

for job in jobs:
    job_title0 = job.find_element(By.CSS_SELECTOR, 'h3').get_attribute('innerText')
    job_title.append(job_title0)

    company_name0 = job.find_element(By.CSS_SELECTOR, 'h4').get_attribute('innerText')
    company_name.append(company_name0)


    location0 = job.find_element(By.CLASS_NAME, 'job-search-card__location').get_attribute('innerText')
    if ("Hamburg" in location0):
        location0 = "Hamburg"
    else:
        location0 = "Other"

    location.append(location0)


    date0 = job.find_element(By.CSS_SELECTOR, 'div>div>time').get_attribute('datetime')
    date.append(date0)

    job_link0 = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
    job_link.append(job_link0)

    #get details
    job_func0=[]
    industries0=[]
    job_click_path = f'/html/body/div/div/main/section[2]/ul/li[{job_counter+1}]/div/div/img'
    try:
        link = job.find_element(By.XPATH, f'/html/body/div/div/main/section[2]/ul/li[{job_counter+1}]/div/a')
        wd.execute_script("arguments[0].style.display = 'none'",link)
        job_click = job.find_element(By.XPATH, job_click_path).click()
        time.sleep(4)
        jd_path = '/html/body/div/div/section/div[2]/div/section/div/div/section/div'
        jd0 = job.find_element(By.XPATH, jd_path).get_attribute('innerText')
        jd0 = re.sub('[^a-zA-Z0-9 \n\.]', '', jd0)
        print(jd0)
        jd.append(jd0)
        seniority_path = '/html/body/div/div/section/div[2]/div/section/div/ul/li/span'
        seniority0 = job.find_element(By.XPATH, seniority_path).get_attribute('innerText')
        print(seniority0)
        seniority.append(seniority0)
        emp_type_path = '/html/body/div/div/section/div[2]/div/section/div/ul/li[2]/span'
        emp_type0 = job.find_element(By.XPATH, emp_type_path).get_attribute('innerText')
        print(emp_type0)
        emp_type.append(emp_type0)
        job_func_path = '/html/body/div/div/section/div[2]/div/section/div/ul/li[3]/span'
        job_func_elements = job.find_elements(By.XPATH, job_func_path)
        for element in job_func_elements:
            job_func0.append(element.get_attribute('innerText'))
            job_func_final = ', '.join(job_func0)
            job_func.append(job_func_final)
            industries_path = '/html/body/div/div/section/div[2]/div/section/div/ul/li[4]/span'
            industries_elements = job.find_elements(By.XPATH, industries_path)
        for element in industries_elements:
            industries0.append(element.get_attribute('innerText'))
            industries_final = ', '.join(industries0)
            industries.append(industries_final)
    except:
        jd.append('Details skipped due to error')
        seniority.append('Details skipped due to error')
        emp_type.append('Details skipped due to error')
        job_func.append('Details skipped due to error')
        industries.append('Details skipped due to error')



    job_counter += 1
    chunk_size -= 1

    if chunk_size == 1:
        a = {
            'Date' : date , 
            'Company': company_name,
            'Title': job_title,
            'Location': location,
            'Description': jd,
            'Level': seniority,
            'Type': emp_type,
            'Function': job_func,
            'Industry': industries,
            'Link': job_link
            }
        
        job_data = pd.DataFrame.from_dict(a, orient='index')
        job_data = job_data.transpose()
        job_data['Description'] = job_data['Description'].str.replace('\n',' ')
        job_data['Description'] = job_data['Description'].str.replace(';',',')
        job_data.to_csv(f'/home/zwnow/Desktop/JobScraper/csvs/jobs{job_counter}.csv', index = False)

        job_title = []
        company_name = []
        location = []
        date = []
        job_link = []
        jd = []
        seniority = []
        emp_type = []
        job_func = []
        industries = []

        chunk_size = 50