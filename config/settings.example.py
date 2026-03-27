# ============================================================
#  config/settings.example.py
#  Copy to config/settings.py and fill in your local values
# ============================================================

# Search keywords (prefix search)
KEYWORDS = [
    "analy",
    "scientist",
]

# Job passes only if its title contains at least one of these
TITLE_FILTERS = [
    "analyst",
    "analytics",
    "scientist",
    "science",
    "analysis",
]

# Job passes if at least one location matches any zone
LOCATION_FILTERS = {
    "remote": ["remote", "anywhere", "virtual"],
    "oregon": ["oregon", "portland", "beaverton", "hillsboro"],
    "bay_area": [
        "san francisco",
        "santa clara",
        "mountain view",
        "palo alto",
        "menlo park",
        "sunnyvale",
        "cupertino",
        "fremont",
        "berkeley",
        "oakland",
        "san jose, ca",
        "san jose, california",
    ],
}

FRESH_ONLY = True
FRESH_DAYS = 3

COMPANIES = [
    {
        "name": "Intel",
        "wd_host": "intel.wd1.myworkdayjobs.com",
        "tenant_id": "intel",
        "tenant_name": "External",
    },
    {
        "name": "Nike",
        "wd_host": "nike.wd1.myworkdayjobs.com",
        "tenant_id": "nike",
        "tenant_name": "nke",
    },
    {
        "name": "NVIDIA",
        "wd_host": "nvidia.wd5.myworkdayjobs.com",
        "tenant_id": "nvidia",
        "tenant_name": "NVIDIAExternalCareerSite",
    },
    {
        "name": "HP",
        "wd_host": "hp.wd5.myworkdayjobs.com",
        "tenant_id": "hp",
        "tenant_name": "ExternalCareerSite",
    },
    {
        "name": "Micron",
        "wd_host": "micron.wd1.myworkdayjobs.com",
        "tenant_id": "micron",
        "tenant_name": "External",
    },
    {
        "name": "Applied Materials",
        "wd_host": "amat.wd1.myworkdayjobs.com",
        "tenant_id": "amat",
        "tenant_name": "External",
    },
    {
        "name": "Workday",
        "wd_host": "workday.wd5.myworkdayjobs.com",
        "tenant_id": "workday",
        "tenant_name": "Workday",
    },
    {
        "name": "Stryker",
        "wd_host": "stryker.wd1.myworkdayjobs.com",
        "tenant_id": "stryker",
        "tenant_name": "StrykerCareers",
    },
    {
        "name": "Capital One",
        "wd_host": "capitalone.wd12.myworkdayjobs.com",
        "tenant_id": "capitalone",
        "tenant_name": "Capital_One",
    },
    {
        "name": "BECU",
        "wd_host": "becu.wd1.myworkdayjobs.com",
        "tenant_id": "becu",
        "tenant_name": "External",
    },
    {
        "name": "Dell",
        "wd_host": "dell.wd1.myworkdayjobs.com",
        "tenant_id": "dell",
        "tenant_name": "External",
    },
    {
        "name": "Salesforce",
        "wd_host": "salesforce.wd12.myworkdayjobs.com",
        "tenant_id": "salesforce",
        "tenant_name": "External_Career_Site",
    },
    {
        "name": "Cisco",
        "wd_host": "cisco.wd5.myworkdayjobs.com",
        "tenant_id": "cisco",
        "tenant_name": "Cisco_Careers",
    },
    {
        "name": "Qualcomm",
        "wd_host": "qualcomm.wd12.myworkdayjobs.com",
        "tenant_id": "qualcomm",
        "tenant_name": "External",
    },
    {
        "name": "Adobe",
        "wd_host": "adobe.wd5.myworkdayjobs.com",
        "tenant_id": "adobe",
        "tenant_name": "external_experienced",
    },
]

# Fill these with your local email settings
EMAIL_ENABLED = True
EMAIL_FROM = "your-email@example.com"
EMAIL_TO = "your-email@example.com"
EMAIL_PASSWORD = "your-app-password"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

MAX_JOBS_PER_COMPANY = 200
PAGE_SIZE = 20
REQUEST_DELAY_SEC = 1.2
FETCH_DETAILS = False
