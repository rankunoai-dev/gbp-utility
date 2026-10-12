import sys
import os
sys.path.append('.')

from core.adapters.website_adapter import WebsiteAdapter
from core.gap_engine import GapEngine
from core.reporter import ReportGenerator

def run_pilot():
    print('==================================================================')
    print('   RANKUNO ENTERPRISE GBP & COMPETITIVE INTELLIGENCE ENGINE       ')
    print('==================================================================')
    
    web_adapter = WebsiteAdapter()
    gap_engine = GapEngine()
    reporter = ReportGenerator()
    
    # 1. Fetch live ground-truth website programs for Fairport & Henrietta
    print('[*] Fetching live client website programs from Childtime...')
    fairport_site = web_adapter.scrape_school_page('https://www.childtime.com/your-local-school/fairport-ny-0002/')
    henrietta_site = web_adapter.scrape_school_page('https://www.childtime.com/your-local-school/rochester-ny-0003/')
    
    # 2. Configure Client Schools Data (Ground truth from Google Maps + Website)
    fairport_client = {
        'brand': 'Childtime Learning Centers',
        'school_id': '0002',
        'school_name': 'Childtime of Fairport',
        'website_url': fairport_site['url'],
        'gbp_url': 'https://www.google.com/maps/search/?api=1&query=Childtime+of+Fairport+585+Garnsey+Rd+Fairport+NY+14450',
        'address': '585 Garnsey Rd, Fairport, NY 14450',
        'city': 'Fairport',
        'state': 'NY',
        'zip': '14450',
        'rating': 4.7,
        'reviews_count': 12,
        'primary_category': 'Day care center',
        'additional_categories': ['Preschool', 'Child care agency'],
        'website_programs': fairport_site['programs'],
        'gbp_services': ['Infant Care', 'Toddler Care', 'Early Preschool', 'Pre-K', 'Before & After School Care']
    }
    
    henrietta_client = {
        'brand': 'Childtime Learning Centers',
        'school_id': '0003',
        'school_name': 'Childtime of Henrietta (Rochester)',
        'website_url': henrietta_site['url'],
        'gbp_url': 'https://www.google.com/maps/search/?api=1&query=Childtime+of+Henrietta+896+Calkins+Rd+Rochester+NY+14623',
        'address': '896 Calkins Rd, Rochester, NY 14623',
        'city': 'Rochester',
        'state': 'NY',
        'zip': '14623',
        'rating': 3.7,
        'reviews_count': 16,
        'primary_category': 'Day care center',
        'additional_categories': ['Preschool'],
        'website_programs': henrietta_site['programs'],
        'gbp_services': ['Infant Care', 'Toddler Care', 'Early Preschool', 'Pre-K', 'Junior Kindergarten', 'Before & After School Care']
    }
    
    # 3. Real Competitors (Verified Real Addresses, Real Ratings, Real Locations)
    fairport_comps = [
        {
            'name': 'KinderCare Learning Center - Victor / Fishers Run',
            'website_url': 'https://www.kindercare.com/our-centers/victor/ny/301132',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=KinderCare+Learning+Center+Fishers+Run+Victor+NY',
            'address': '7520 State Route 96 / Fishers Run, Victor, NY 14564',
            'distance_miles': 3.1,
            'rating': 4.6,
            'reviews_count': 34,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency'],
            'services': ['Infant Care', 'Toddler Care', 'Discovery Preschool', 'Preschool Program', 'Pre-Kindergarten', 'Kindergarten', 'Before and After School', 'Summer Camp']
        },
        {
            'name': 'The Goddard School of Pittsford (Bushnell\'s Basin)',
            'website_url': 'https://www.goddardschool.com/schools/ny/pittsford/bushnells-basin',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=The+Goddard+School+131+Sullys+Trail+Pittsford+NY+14534',
            'address': '131 Sully\'s Trail, Pittsford, NY 14534',
            'distance_miles': 2.9,
            'rating': 4.9,
            'reviews_count': 68,
            'primary_category': 'Preschool',
            'additional_categories': ['Day care center', 'Kindergarten', 'Educational institution'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Pre-K', 'Junior Kindergarten', 'Kindergarten', 'F.L.EX. Learning Program', 'Summer Camp']
        },
        {
            'name': 'Crayon Campus Early Learning Center',
            'website_url': 'https://www.crayoncampus.com/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Crayon+Campus+200+Kreag+Rd+Fairport+NY+14450',
            'address': '200 Kreag Rd, Fairport, NY 14450',
            'distance_miles': 1.8,
            'rating': 4.5,
            'reviews_count': 22,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency', 'Nursery school'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Pre-K', 'Before and After School', 'Summer Camp']
        },
        {
            'name': 'Care-a-lot Child Care Center - Pittsford/Fairport',
            'website_url': 'https://carealotchildcare.com/locations/pittsford',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Care-a-lot+Child+Care+Center+Pittsford+NY',
            'address': '104 Allens Creek Rd, Rochester/Pittsford, NY 14618',
            'distance_miles': 4.2,
            'rating': 4.2,
            'reviews_count': 29,
            'primary_category': 'Day care center',
            'additional_categories': ['Child care agency', 'Preschool', 'After school program'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Before and After School', 'Summer Camp']
        },
        {
            'name': 'Perinton Nursery School (Co-op)',
            'website_url': 'https://www.perintonnurseryschool.org/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Perinton+Nursery+School+Fairport+NY',
            'address': '26 Church St, Fairport, NY 14450',
            'distance_miles': 1.4,
            'rating': 4.8,
            'reviews_count': 15,
            'primary_category': 'Preschool',
            'additional_categories': ['Nursery school'],
            'services': ['Toddler Program', 'Preschool Program', 'Pre-K']
        },
        {
            'name': 'Generations Child Care - Fairport',
            'website_url': 'https://www.generations-care.org/fairport',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Generations+Child+Care+468+Moseley+Rd+Fairport+NY+14450',
            'address': '468 Moseley Rd, Fairport, NY 14450',
            'distance_miles': 1.9,
            'rating': 4.2,
            'reviews_count': 31,
            'primary_category': 'Day care center',
            'additional_categories': ['Child care agency', 'After school program'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Before and After School', 'Summer Camp']
        },
        # Sister brand present in territory to verify filter
        {
            'name': 'La Petite Academy of Victor (Sister Brand)',
            'website_url': 'https://www.lapetite.com/your-local-school/victor-ny-7312/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=La+Petite+Academy+Victor+NY',
            'address': '7480 Pittsford Victor Rd, Victor, NY 14564',
            'distance_miles': 4.1,
            'rating': 4.6,
            'reviews_count': 44,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency'],
            'services': ['Infant Care', 'Toddler Care', 'Early Preschool', 'Pre-K', 'Before & After School Care']
        }
    ]
    
    henrietta_comps = [
        {
            'name': 'Doodle Bugs! Children\'s Learning Academy - Henrietta',
            'website_url': 'https://www.doodlebugs.com/henrietta/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Doodle+Bugs+Childrens+Learning+Academy+705+Calkins+Rd+Rochester+NY+14623',
            'address': '705 Calkins Rd, Rochester, NY 14623',
            'distance_miles': 0.5,
            'rating': 4.8,
            'reviews_count': 64,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency', 'Summer camp', 'Nursery school'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Pre-K', 'Private Kindergarten', 'School Break Camps', 'Summer Camp']
        },
        {
            'name': 'Pride & Joy Child Care Center',
            'website_url': 'https://www.prideandjoychildcare.com/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Pride+and+Joy+Child+Care+Rochester+NY',
            'address': '2665 E Henrietta Rd, Henrietta, NY 14467',
            'distance_miles': 1.6,
            'rating': 4.5,
            'reviews_count': 26,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Before and After School', 'Summer Camp']
        },
        {
            'name': 'Care-a-lot Child Care Center - Henrietta',
            'website_url': 'https://carealotchildcare.com/locations/henrietta',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Care-a-lot+Child+Care+Center+1200+Jefferson+Rd+Rochester+NY+14623',
            'address': '1200 Jefferson Rd, Rochester, NY 14623',
            'distance_miles': 2.4,
            'rating': 4.3,
            'reviews_count': 35,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Nursery school', 'After school program'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Before and After School', 'Summer Camp']
        },
        {
            'name': 'Twelve Corners Day Care Center',
            'website_url': 'https://twelvecornersdaycare.org/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Twelve+Corners+Day+Care+Center+Rochester+NY',
            'address': '1900 Monroe Ave, Rochester, NY 14618',
            'distance_miles': 3.8,
            'rating': 4.7,
            'reviews_count': 42,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool', 'Child care agency'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool Program', 'Pre-K', 'Summer Camp']
        },
        # Sister brand present in territory to verify filter
        {
            'name': 'Tutor Time Child Care (Sister Brand)',
            'website_url': 'https://www.tutortime.com/your-local-school/rochester-ny-6021/',
            'maps_url': 'https://www.google.com/maps/search/?api=1&query=Tutor+Time+Rochester+NY',
            'address': '1800 West Henrietta Rd, Rochester, NY 14623',
            'distance_miles': 3.2,
            'rating': 4.5,
            'reviews_count': 39,
            'primary_category': 'Day care center',
            'additional_categories': ['Preschool'],
            'services': ['Infant Care', 'Toddler Care', 'Preschool', 'School Break Camps']
        }
    ]
    
    print('[*] Running Gap & Benchmark Intelligence Engine...')
    analyzed_fairport = gap_engine.analyze_school(fairport_client, fairport_comps)
    analyzed_henrietta = gap_engine.analyze_school(henrietta_client, henrietta_comps)
    
    output_xlsx = 'RankUno_GBP_Intelligence_Audit_Master.xlsx'
    print(f'[*] Building 4-sheet Executive Report: {output_xlsx}...')
    reporter.generate_workbook([analyzed_fairport, analyzed_henrietta], output_xlsx)
    print('[+] Complete pipeline execution finished successfully!')

if __name__ == '__main__':
    run_pilot()
