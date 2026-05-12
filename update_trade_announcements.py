from pathlib import Path
import json, re
from datetime import date
import requests
from bs4 import BeautifulSoup

OUT = Path(__file__).resolve().parent
DATA = OUT / 'trade_announcements_data.json'

SEEDS = [
    {'category':'Apprenticeship','region':'New York City','sponsor':'LIUNA Local 731 Training Fund','posted':'NYSDOL listing','opening_date':'See NYSDOL','closing_date':'See NYSDOL','details_url':'https://dol.ny.gov/apprenticeship/apprenticeship-announcements','type':'Registered apprenticeship','funding':'Earn while you learn / training generally at no cost','match':['apprenticeship announcements','results found']},
    {'category':'Apprenticeship','region':'New York City','sponsor':'Plumbers Local # 1 JAC','posted':'NYSDOL listing','opening_date':'See NYSDOL','closing_date':'See NYSDOL','details_url':'https://dol.ny.gov/apprenticeship/apprenticeship-announcements','type':'Registered apprenticeship','funding':'Earn while you learn / training generally at no cost','match':['apprenticeship announcements','results found']},
    {'category':'Apprenticeship','region':'Westchester / Hudson Valley','sponsor':'Westchester-Fairfield JEATC LU #3 IBEW','posted':'NYSDOL listing','opening_date':'See NYSDOL','closing_date':'See NYSDOL','details_url':'https://dol.ny.gov/apprenticeship/apprenticeship-announcements','type':'Registered apprenticeship','funding':'Earn while you learn / training generally at no cost','match':['apprenticeship announcements','results found']},
    {'category':'Training','region':'New York City','sponsor':'LaGuardia Community College + Building Skills New York + Positive Workforce','posted':'Program announcement','opening_date':'See provider','closing_date':'Varies by cohort','details_url':'https://www.laguardia.edu/news/building-skills-new-york-laguardia-community-college-launch-free-training-to-expand-clean-energy-workforce/','type':'CUNY tuition-free HVAC training','funding':'Tuition-free / NYSERDA-funded','match':['tuition-free','hvac','nyserda']},
    {'category':'Apprenticeship','region':'New York City','sponsor':'BMCC Aon Apprenticeship Program','posted':'Recruitment timeline published','opening_date':'Check BMCC','closing_date':'Varies','details_url':'https://www.bmcc.cuny.edu/academics/experiential/apprenticeship-programs/apprenticeships-at-bmcc/','type':'CUNY employer-paid apprenticeship','funding':'Salary + 100% tuition, fees, and books paid','match':['salary','tuition','books']},
    {'category':'Training','region':'New York City','sponsor':'College of Staten Island Free 7-Week EPA-608 HVAC Training','posted':'Program announcement','opening_date':'See provider','closing_date':'Limited spaces','details_url':'https://csitoday.com/2025/01/free-7-week-hvac-training-program-now-available-at-csi/','type':'CUNY free short program','funding':'Free of charge','match':['free','7-week','epa']},
    {'category':'Training','region':'New York City','sponsor':'Building Skills NY NCCER Level 1 Training','posted':'Provider listing','opening_date':'Check current intake','closing_date':'Varies by cohort','details_url':'https://buildingskillsny.org/nccer-training/','type':'Free workforce training','funding':'No-cost','match':['no-cost','hvac','electrical']},
    {'category':'Training','region':'Westchester / Hudson Valley','sponsor':'Healthy Home Academy Heat Pump Installation Training','posted':'Program page','opening_date':'Check provider schedule','closing_date':'Varies by cohort','details_url':'https://sustainablewestchester.org/clean-energy-workforce-program/','type':'Free workforce training','funding':'No tuition','match':['no tuition','heat pump','epa 608']},
    {'category':'Scholarship','region':'New York State','sponsor':'UTUIA Trade Scholarships','posted':'Scholarship page','opening_date':'Check provider','closing_date':'Varies','details_url':'https://utuia.org/trade-scholarships/','type':'Scholarship','funding':'$2,000 renewable scholarship','match':['trade scholarships','$2,000','renewable']},
    {'category':'Scholarship','region':'New York State','sponsor':'NYHA Trade School Scholarship','posted':'Scholarship page','opening_date':'Check provider','closing_date':'Varies','details_url':'https://www.nyhousing.org/nyha-scholarship','type':'Scholarship','funding':'Tuition, books, and supplies support','match':['trade school','tuition','hvac']},
    {'category':'Training','region':'New York City','sponsor':'Sea Education New York Maritime Safety and Offshore Wind Training','posted':'Program page','opening_date':'Apply online / choose session','closing_date':'Varies by cohort','details_url':'https://www.seaeducation-ny.com/our-program','type':'Free maritime entry-level training','funding':'100% free + $1,000 stipend','match':['100% free','$1,000 stipend','stcw']},
    {'category':'Training','region':'New York City','sponsor':'SIU Paul Hall Center Unlicensed Apprentice Program','posted':'Entry program page','opening_date':'See provider','closing_date':'Rolling / see provider','details_url':'https://www.seafarers.org/training-and-careers/jobs/entry-program/','type':'Free maritime entry-level training','funding':'Free classes, meals, and lodging + guaranteed first job','match':['free training','guaranteed first job','lodging']},
    {'category':'Job','region':'New York City','sponsor':'Workforce1 Career Centers','posted':'Ongoing city service','opening_date':'Open now','closing_date':'Rolling','details_url':'https://www.nyc.gov/employment/programs/workforce1','type':'Job search and free training access','funding':'Free city service','match':['free training','career centers','job opportunities']},
    {'category':'Job','region':'New York City','sponsor':'City of New York Jobs - Marine Oiler','posted':'Job posting','opening_date':'See job posting','closing_date':'See job posting','details_url':'https://cityjobs.nyc.gov/job/marine-oiler-in-staten-island-jid-31942','type':'Entry-level maritime-related job','funding':'Paid city job','match':['marine oiler','staten island','merchant mariner']},
    {'category':'Job','region':'New York City','sponsor':'Classic Harbor Line / Maritime Opportunities','posted':'Job board page','opening_date':'Check current openings','closing_date':'Rolling','details_url':'https://www.docknyc.com/job-search','type':'Maritime job board','funding':'Paid job listings','match':['maritime job opportunities','job opportunities']},
    {'category':'Job','region':'New York City','sponsor':'MTA Skilled Trades Positions','posted':'Always hiring page','opening_date':'Open now','closing_date':'Rolling','details_url':'https://www.mta.info/careers/skilled-trades-positions','type':'Trade job board','funding':'Paid job listings','match':['skilled trades positions','always hiring']}
]

def clean_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    return re.sub(r'\\s+', ' ', soup.get_text(' ', strip=True)).lower()

items = []
for seed in SEEDS:
    try:
        r = requests.get(seed['details_url'], timeout=20, headers={'User-Agent':'Mozilla/5.0'})
        if r.ok:
            txt = clean_text(r.text)
            ok = any(m.lower() in txt for m in seed['match'])
            status = 'Checked today' if ok else 'Checked today; review wording'
        else:
            status = f'HTTP {r.status_code}'
    except Exception as e:
        status = f'Check failed: {type(e).__name__}'
    row = {k:v for k,v in seed.items() if k != 'match'}
    row['status'] = status
    items.append(row)

payload = {'updated': str(date.today()), 'items': items}
DATA.write_text(json.dumps(payload, indent=2), encoding='utf-8')
print('Updated', DATA)
