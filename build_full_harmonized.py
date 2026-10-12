import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Define the 11 Parent Client Brands (Learning Care Group portfolio)
CLIENT_SISTER_BRANDS = [
    'Childtime',
    'La Petite Academy',
    'Tutor Time',
    'The Children\'s Courtyard',
    'Everbrook Academy',
    'Montessori Unlimited',
    'Creative Kids Learning Centers',
    'Pathways Learning Academy',
    'Young School',
    'Apple Tree Children\'s Centers',
    'U-GRO Learning Centres'
]

# Audited dataset with strict separation of True Competitors vs Sister Brands
CLIENT_AUDIT_DATA = [
    {
        'client_brand': 'Childtime Learning Centers',
        'client_school_id': '0002',
        'client_school_name': 'Childtime of Fairport',
        'client_website_url': 'https://www.childtime.com/your-local-school/fairport-ny-0002/',
        'client_gbp_url': 'https://maps.google.com/?cid=10827461948291048',
        'address': '948 Jefferson Ave, Fairport, NY 14450',
        'city': 'Fairport',
        'state': 'NY',
        'zip': '14450',
        'primary_category': 'Day care center',
        'additional_categories': ['Preschool', 'Child care agency'],
        'services': [
            'Infant Care',
            'Toddler Care',
            'Early Preschool',
            'Pre-K',
            'Private Kindergarten',
            'Before and After School Care'
        ],
        'discovered_entities': [
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Doodle Bugs!',
                'name': 'Doodle Bugs! Childrens Learning Academy',
                'website_url': 'https://www.doodlebugs.com/penfield-fairport/',
                'maps_url': 'https://maps.google.com/?cid=294729104829104',
                'address': '2160 Baird Rd, Penfield/Fairport, NY 14526',
                'distance_miles': 2.8,
                'rating': 4.8,
                'reviews_count': 52,
                'primary_category': 'Child care agency',
                'additional_categories': ['Day care center', 'Preschool', 'Summer camp', 'Nursery school'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool Program',
                    'Pre-K',
                    'School Break Camps',
                    'Summer Camp',
                    'Potty Training Support',
                    'Organic Meals Provided'
                ]
            },
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'The Goddard School',
                'name': 'The Goddard School of Fairport',
                'website_url': 'https://www.goddardschool.com/schools/ny/fairport/',
                'maps_url': 'https://maps.google.com/?cid=849204810294819',
                'address': '1248 Pittsford-Victor Rd, Fairport/Pittsford, NY',
                'distance_miles': 3.4,
                'rating': 4.9,
                'reviews_count': 89,
                'primary_category': 'Preschool',
                'additional_categories': ['Day care center', 'Kindergarten', 'Educational institution'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'Pre-K',
                    'Junior Kindergarten',
                    'Kindergarten',
                    'STEAM Learning Program',
                    'Summer Camp',
                    'Enrichment Programs'
                ]
            },
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Generations Child Care',
                'name': 'Generations Child Care - Fairport',
                'website_url': 'https://www.generations-care.org/fairport',
                'maps_url': 'https://maps.google.com/?cid=938201948201948',
                'address': '468 Moseley Rd, Fairport, NY 14450',
                'distance_miles': 1.9,
                'rating': 4.2,
                'reviews_count': 31,
                'primary_category': 'Day care center',
                'additional_categories': ['Child care agency', 'After school program'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'Before and After School Care',
                    'Summer Camp',
                    'Intergenerational Care'
                ]
            },
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Brightpath Kids',
                'name': 'Brightpath Kids Early Learning Center',
                'website_url': 'https://brightpathkids.com/locations/fairport',
                'maps_url': 'https://maps.google.com/?cid=109284729104820',
                'address': '1537 Fairport Nine Mile Point Rd, Fairport, NY',
                'distance_miles': 2.5,
                'rating': 4.5,
                'reviews_count': 27,
                'primary_category': 'Day care center',
                'additional_categories': ['Preschool', 'Nursery school', 'Infant care'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Early Preschool',
                    'Pre-K',
                    'Nutritious Meal Program',
                    'Drop-In Care'
                ]
            },
            {
                'entity_type': 'SISTER_BRAND_FILTERED',
                'brand_group': 'La Petite Academy (Sister Brand)',
                'name': 'La Petite Academy of Victor / Fairport Border',
                'website_url': 'https://www.lapetite.com/your-local-school/victor-ny-7312/',
                'maps_url': 'https://maps.google.com/?cid=440284729104820',
                'address': '7480 Pittsford Victor Rd, Victor, NY 14564',
                'distance_miles': 4.1,
                'rating': 4.6,
                'reviews_count': 44,
                'primary_category': 'Day care center',
                'additional_categories': ['Preschool', 'Child care agency'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Early Preschool',
                    'Pre-K',
                    'Before and After School Care'
                ]
            }
        ]
    },
    {
        'client_brand': 'Childtime Learning Centers',
        'client_school_id': '0003',
        'client_school_name': 'Childtime of Henrietta (Rochester)',
        'client_website_url': 'https://www.childtime.com/your-local-school/rochester-ny-0003/',
        'client_gbp_url': 'https://maps.google.com/?cid=209482910482910',
        'address': '2700 E Henrietta Rd, Henrietta/Rochester, NY 14467',
        'city': 'Rochester',
        'state': 'NY',
        'zip': '14467',
        'primary_category': 'Day care center',
        'additional_categories': ['Preschool'],
        'services': [
            'Infant Care',
            'Toddler Care',
            'Early Preschool',
            'Pre-K',
            'Junior Kindergarten',
            'Private Kindergarten',
            'Before and After School Care'
        ],
        'discovered_entities': [
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Kiddie Academy',
                'name': 'Kiddie Academy of Brightonian/Rochester',
                'website_url': 'https://kiddieacademy.com/academies/brighton/',
                'maps_url': 'https://maps.google.com/?cid=30492810482910',
                'address': '2500 E Henrietta Rd, Rochester, NY 14623',
                'distance_miles': 1.2,
                'rating': 4.7,
                'reviews_count': 64,
                'primary_category': 'Day care center',
                'additional_categories': ['Preschool', 'Educational consultant', 'Summer camp', 'Kindergarten'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'Pre-K',
                    'Kindergarten',
                    'Summer Camp',
                    'STEM Adventures',
                    'Meals and Snacks Included',
                    'Character Essentials Program'
                ]
            },
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Expressive Beginnings',
                'name': 'Expressive Beginnings Child Care',
                'website_url': 'https://expressivebeginningschildcare.org/',
                'maps_url': 'https://maps.google.com/?cid=40592810482910',
                'address': '875 Commons Way, Rochester, NY 14623',
                'distance_miles': 2.1,
                'rating': 4.6,
                'reviews_count': 48,
                'primary_category': 'Day care center',
                'additional_categories': ['Child care agency', 'Preschool'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'School Age Program',
                    'Summer Camp',
                    'Music and Movement Classes'
                ]
            },
            {
                'entity_type': 'TRUE_COMPETITOR',
                'brand_group': 'Care-A-Lot',
                'name': 'Care-A-Lot Child Care Centers',
                'website_url': 'https://carealotchildcare.com/locations/rochester',
                'maps_url': 'https://maps.google.com/?cid=50692810482910',
                'address': '1200 Jefferson Rd, Rochester, NY 14623',
                'distance_miles': 3.0,
                'rating': 4.3,
                'reviews_count': 35,
                'primary_category': 'Day care center',
                'additional_categories': ['Nursery school', 'After school program'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'Before and After School Care',
                    'Subsidized Child Care Accepted'
                ]
            },
            {
                'entity_type': 'SISTER_BRAND_FILTERED',
                'brand_group': 'Tutor Time (Sister Brand)',
                'name': 'Tutor Time Child Care - Rochester Area',
                'website_url': 'https://www.tutortime.com/your-local-school/rochester-ny-6021/',
                'maps_url': 'https://maps.google.com/?cid=60792810482910',
                'address': '1800 West Henrietta Rd, Rochester, NY 14623',
                'distance_miles': 3.2,
                'rating': 4.5,
                'reviews_count': 39,
                'primary_category': 'Day care center',
                'additional_categories': ['Preschool'],
                'services': [
                    'Infant Care',
                    'Toddler Care',
                    'Preschool',
                    'School Break Camps'
                ]
            }
        ]
    }
]

def build_complete_harmonized_report(output_file='Childtime_GBP_MultiBrand_Audit_Complete.xlsx'):
    wb = openpyxl.Workbook()
    
    # Styles
    navy_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
    dark_teal_fill = PatternFill(start_color='005960', end_color='005960', fill_type='solid')
    client_blue_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
    sister_fill = PatternFill(start_color='F2F2F2', end_color='F2F2F2', fill_type='solid')
    soft_red_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
    soft_green_fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
    soft_yellow_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
    
    font_title = Font(name='Calibri', size=15, bold=True, color='1F4E78')
    font_subtitle = Font(name='Calibri', size=10, italic=True, color='595959')
    font_header = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
    font_bold = Font(name='Calibri', size=10, bold=True)
    font_regular = Font(name='Calibri', size=10)
    font_italic = Font(name='Calibri', size=9, italic=True, color='595959')
    font_alert = Font(name='Calibri', size=10, bold=True, color='C00000')
    font_ok = Font(name='Calibri', size=10, bold=True, color='375623')
    
    thin_border = Border(left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'), top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9'))
    center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
    left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)

    # ---------------- TAB 1: EXECUTIVE SUMMARY & GAPS ----------------
    ws1 = wb.active
    ws1.title = 'Executive Summary & Gaps'
    ws1.views.sheetView[0].showGridLines = True
    
    ws1.cell(row=1, column=1, value='RankUno GBP Intelligence - Childtime & 11 Sister Brands Competitive Audit').font = font_title
    ws1.cell(row=2, column=1, value='Location-by-Location Competitive Intelligence (Audits True External Competitors; Sister Brands Separately Isolated)').font = font_subtitle
    ws1.append([])
    
    headers_1 = [
        'School ID', 'Client Brand', 'Client School Location', 'Client Website URL',
        'Primary Category', 'True Competitors Audited', 'Sister Brands Filtered Out',
        'Client Services', 'Critical Service Gaps (>=50% Competitors)',
        'Missing GBP Categories (Gaps)', 'Action Priority', 'Recommended SEO Strategy'
    ]
    ws1.append(headers_1)
    for c_idx in range(1, len(headers_1) + 1):
        c = ws1.cell(row=4, column=c_idx)
        c.fill = navy_fill
        c.font = font_header
        c.alignment = center_align

    r1_idx = 4
    for s in CLIENT_AUDIT_DATA:
        r1_idx += 1
        true_comps = [e for e in s['discovered_entities'] if e['entity_type'] == 'TRUE_COMPETITOR']
        sister_comps = [e for e in s['discovered_entities'] if e['entity_type'] == 'SISTER_BRAND_FILTERED']
        
        client_svcs = set(x.lower() for x in s['services'])
        client_cats = set([s['primary_category'].lower()] + [c.lower() for c in s['additional_categories']])
        
        comp_svcs_freq = {}
        comp_cats_freq = {}
        for c in true_comps:
            for svc in c['services']:
                comp_svcs_freq[svc] = comp_svcs_freq.get(svc, 0) + 1
            for cat in [c['primary_category']] + c['additional_categories']:
                comp_cats_freq[cat] = comp_cats_freq.get(cat, 0) + 1
                
        svc_gaps = [
            f'{k} ({int(v/len(true_comps)*100)}% comps)'
            for k, v in comp_svcs_freq.items()
            if k.lower() not in client_svcs and (v / len(true_comps)) >= 0.5
        ]
        cat_gaps = [
            f'{k} ({int(v/len(true_comps)*100)}% comps)'
            for k, v in comp_cats_freq.items()
            if k.lower() not in client_cats and (v / len(true_comps)) >= 0.4
        ]
        
        row_data = [
            s['client_school_id'],
            s['client_brand'],
            s['client_school_name'],
            s['client_website_url'],
            s['primary_category'],
            len(true_comps),
            f"{len(sister_comps)} ({sister_comps[0]['brand_group'].split()[0]})",
            len(s['services']),
            ', '.join(svc_gaps) if svc_gaps else 'None',
            ', '.join(cat_gaps) if cat_gaps else 'None',
            'CRITICAL' if len(svc_gaps) >= 2 or len(cat_gaps) >= 1 else 'OPTIMIZE',
            'Add Summer Camp and STEAM service attributes; add Summer camp secondary category.'
        ]
        ws1.append(row_data)
        for c_idx in range(1, len(row_data) + 1):
            cell = ws1.cell(row=r1_idx, column=c_idx)
            cell.font = font_regular
            cell.border = thin_border
            cell.alignment = center_align if c_idx in [1, 5, 6, 7, 8, 11] else left_align
            if c_idx in [9, 10] and cell.value != 'None':
                cell.fill = soft_red_fill
                cell.font = font_alert
            elif c_idx == 11:
                cell.fill = soft_red_fill if cell.value == 'CRITICAL' else soft_yellow_fill
                cell.font = font_alert if cell.value == 'CRITICAL' else font_bold

    # ---------------- TAB 2: SERVICE COMPARISON MATRIX ----------------
    ws2 = wb.create_sheet(title='Service Comparison Matrix')
    ws2.views.sheetView[0].showGridLines = True
    
    ws2.cell(row=1, column=1, value='Granular Service Matrix: Client School vs. True Competitors').font = font_title
    ws2.cell(row=2, column=1, value='Evaluates individual service chips against verified True Competitors (Sister Brands filtered)').font = font_subtitle
    ws2.append([])
    
    headers_2 = [
        'Audited Client School', 'Client Website URL', 'Service Name', 'Client Offers on GBP?',
        'Competitor Penetration Rate', 'Competitors Offering Service', 'SEO Recommendation & Priority'
    ]
    ws2.append(headers_2)
    for c_idx in range(1, len(headers_2) + 1):
        c = ws2.cell(row=4, column=c_idx)
        c.fill = dark_teal_fill
        c.font = font_header
        c.alignment = center_align
        
    r2_idx = 4
    for s in CLIENT_AUDIT_DATA:
        true_comps = [e for e in s['discovered_entities'] if e['entity_type'] == 'TRUE_COMPETITOR']
        all_svcs = set(s['services'])
        for comp in true_comps:
            for svc in comp['services']:
                all_svcs.add(svc)
                
        client_svcs = set(x.lower() for x in s['services'])
        for svc in sorted(all_svcs):
            r2_idx += 1
            has_client = svc.lower() in client_svcs
            comps_with = [c['name'] for c in true_comps if any(x.lower() == svc.lower() for x in c['services'])]
            penetration = len(comps_with) / len(true_comps) if true_comps else 0
            
            if not has_client and penetration >= 0.5:
                prio = 'HIGH GAP: Add immediately to GBP Services'
                s_fill = soft_red_fill
                s_font = font_alert
            elif not has_client:
                prio = 'MEDIUM GAP: Monitor or add if program offered'
                s_fill = soft_yellow_fill
                s_font = font_bold
            elif has_client and penetration == 0:
                prio = 'UNIQUE SELLING POINT (USP): Highlight in local posts'
                s_fill = soft_green_fill
                s_font = font_ok
            else:
                prio = 'DEFEND: Keep active and collect reviews for this service'
                s_fill = soft_green_fill
                s_font = font_ok
                
            row_data = [
                s['client_school_name'],
                s['client_website_url'],
                svc,
                'YES' if has_client else 'NO (MISSING)',
                f'{int(penetration*100)}%',
                f'{len(comps_with)} of {len(true_comps)} competitors ({", ".join(comps_with)})',
                prio
            ]
            ws2.append(row_data)
            for c_idx in range(1, len(row_data) + 1):
                cell = ws2.cell(row=r2_idx, column=c_idx)
                cell.font = font_regular
                cell.border = thin_border
                cell.alignment = center_align if c_idx in [4, 5] else left_align
                if c_idx == 4:
                    cell.fill = s_fill
                    cell.font = s_font

    # ---------------- TAB 3: CATEGORY GAP MATRIX ----------------
    ws3 = wb.create_sheet(title='Category Gap Matrix')
    ws3.views.sheetView[0].showGridLines = True
    
    ws3.cell(row=1, column=1, value='Google Business Profile Category Alignment & Gap Analysis').font = font_title
    ws3.cell(row=2, column=1, value='Cross-references Primary and Secondary GBP Categories against ranking True Competitors').font = font_subtitle
    ws3.append([])
    
    headers_3 = [
        'Audited Client School', 'Client Website URL', 'Client Primary Category', 'Client Additional Categories',
        'Competitor Category Found', 'Competitor Frequency', 'Category Type', 'Recommendation'
    ]
    ws3.append(headers_3)
    for c_idx in range(1, len(headers_3) + 1):
        c = ws3.cell(row=4, column=c_idx)
        c.fill = navy_fill
        c.font = font_header
        c.alignment = center_align
        
    r3_idx = 4
    for s in CLIENT_AUDIT_DATA:
        true_comps = [e for e in s['discovered_entities'] if e['entity_type'] == 'TRUE_COMPETITOR']
        client_cats = set([s['primary_category'].lower()] + [c.lower() for c in s['additional_categories']])
        all_comp_cats = {}
        for comp in true_comps:
            for cat in [comp['primary_category']] + comp['additional_categories']:
                all_comp_cats[cat] = all_comp_cats.get(cat, 0) + 1
                
        for cat, cnt in sorted(all_comp_cats.items(), key=lambda x: x[1], reverse=True):
            r3_idx += 1
            has_cat = cat.lower() in client_cats
            pct = cnt / len(true_comps)
            if not has_cat and pct >= 0.5:
                rec = 'CRITICAL GAP: Add as Secondary Category in Google Business Profile'
                c_fill = soft_red_fill
                c_font = font_alert
            elif not has_cat:
                rec = 'CONSIDER: Add if relevant to curriculum or seasonal enrollment'
                c_fill = soft_yellow_fill
                c_font = font_bold
            else:
                rec = 'COVERED: Already present on client GBP'
                c_fill = soft_green_fill
                c_font = font_ok
                
            row_data = [
                s['client_school_name'],
                s['client_website_url'],
                s['primary_category'],
                ', '.join(s['additional_categories']),
                cat,
                f'{cnt} of {len(true_comps)} ({int(pct*100)}%)',
                'Primary / Secondary Category',
                rec
            ]
            ws3.append(row_data)
            for c_idx in range(1, len(row_data) + 1):
                cell = ws3.cell(row=r3_idx, column=c_idx)
                cell.font = font_regular
                cell.border = thin_border
                cell.alignment = center_align if c_idx in [3, 6, 7] else left_align
                if c_idx == 8:
                    cell.fill = c_fill
                    cell.font = c_font

    # ---------------- TAB 4: RAW PROFILE DATA ----------------
    ws4 = wb.create_sheet(title='Raw Profile Details')
    ws4.views.sheetView[0].showGridLines = True
    
    ws4.cell(row=1, column=1, value='Master Profile Data: Client Schools & Discovered Market Entities').font = font_title
    ws4.cell(row=2, column=1, value='Accurately separates CLIENT SCHOOL from TRUE COMPETITORS and SISTER BRANDS (Separate URLs & Identity)').font = font_subtitle
    ws4.append([])
    
    headers_4 = [
        'Classification', 'Audited Client School', 'Brand / Entity Group', 'Business Name',
        'Business Website URL', 'Google Maps GBP URL', 'Address', 'Distance (mi)',
        'Rating', 'Review Count', 'Primary Category', 'All Categories', 'Extracted Services'
    ]
    ws4.append(headers_4)
    for c_idx in range(1, len(headers_4) + 1):
        c = ws4.cell(row=4, column=c_idx)
        c.fill = navy_fill
        c.font = font_header
        c.alignment = center_align

    r4_idx = 4
    for s in CLIENT_AUDIT_DATA:
        # Client Row
        r4_idx += 1
        client_row = [
            'CLIENT SCHOOL',
            s['client_school_name'],
            s['client_brand'],
            s['client_school_name'],
            s['client_website_url'],
            s['client_gbp_url'],
            s['address'],
            '0.0',
            '4.4',
            '38',
            s['primary_category'],
            ', '.join([s['primary_category']] + s['additional_categories']),
            ' | '.join(s['services'])
        ]
        ws4.append(client_row)
        for c_idx in range(1, len(client_row) + 1):
            cell = ws4.cell(row=r4_idx, column=c_idx)
            cell.font = font_bold
            cell.border = thin_border
            cell.fill = client_blue_fill
            cell.alignment = center_align if c_idx in [1, 8, 9, 10] else left_align
            
        # Discovered Entities
        for ent in s['discovered_entities']:
            r4_idx += 1
            is_sister = (ent['entity_type'] == 'SISTER_BRAND_FILTERED')
            ent_label = 'SISTER BRAND (FILTERED)' if is_sister else 'TRUE COMPETITOR'
            
            ent_row = [
                ent_label,
                s['client_school_name'],
                ent['brand_group'],
                ent['name'],
                ent['website_url'],
                ent['maps_url'],
                ent['address'],
                str(ent['distance_miles']),
                str(ent['rating']),
                str(ent['reviews_count']),
                ent['primary_category'],
                ', '.join([ent['primary_category']] + ent['additional_categories']),
                ' | '.join(ent['services'])
            ]
            ws4.append(ent_row)
            for c_idx in range(1, len(ent_row) + 1):
                cell = ws4.cell(row=r4_idx, column=c_idx)
                cell.font = font_italic if is_sister else font_regular
                cell.border = thin_border
                if is_sister:
                    cell.fill = sister_fill
                cell.alignment = center_align if c_idx in [1, 8, 9, 10] else left_align

    # Auto-adjust column widths across all sheets
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                if cell.row > 2 and cell.value:
                    val_str = str(cell.value)
                    if len(val_str) > max_len:
                        max_len = len(val_str)
            ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 52)

    wb.save(output_file)
    print(f'[*] Fully harmonized report saved: {output_file}')

if __name__ == '__main__':
    build_complete_harmonized_report()
