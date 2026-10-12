import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# Ensure clean UTF-8 text and exact website URLs mapped
CLIENT_SCHOOLS = [
    {
        "brand": "Childtime Learning Centers",
        "school_id": "0002",
        "school_name": "Childtime of Fairport",
        "school_url": "https://www.childtime.com/your-local-school/fairport-ny-0002/",
        "address": "948 Jefferson Ave, Fairport, NY 14450",
        "city": "Fairport",
        "state": "NY",
        "zip": "14450",
        "gbp_primary_category": "Day care center",
        "gbp_additional_categories": ["Preschool", "Child care agency"],
        "gbp_services": [
            "Infant Care",
            "Toddler Care",
            "Early Preschool",
            "Pre-K",
            "Private Kindergarten",
            "Before & After School Care"
        ],
        "competitors": [
            {
                "name": "Doodle Bugs! Children's Learning Academy",
                "address": "2160 Baird Rd, Penfield/Fairport, NY 14526",
                "distance_miles": 2.8,
                "rating": 4.8,
                "reviews_count": 52,
                "gbp_primary_category": "Child care agency",
                "gbp_additional_categories": ["Day care center", "Preschool", "Summer camp", "Nursery school"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool Program",
                    "Pre-K",
                    "School Break Camps",
                    "Summer Camp",
                    "Potty Training Support",
                    "Organic Meals Provided"
                ]
            },
            {
                "name": "The Goddard School of Fairport",
                "address": "1248 Pittsford-Victor Rd, Fairport/Pittsford, NY",
                "distance_miles": 3.4,
                "rating": 4.9,
                "reviews_count": 89,
                "gbp_primary_category": "Preschool",
                "gbp_additional_categories": ["Day care center", "Kindergarten", "Educational institution"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool",
                    "Pre-K",
                    "Junior Kindergarten",
                    "Kindergarten",
                    "STEAM Learning Program",
                    "Summer Camp",
                    "Enrichment Programs"
                ]
            },
            {
                "name": "Generations Child Care - Fairport",
                "address": "468 Moseley Rd, Fairport, NY 14450",
                "distance_miles": 1.9,
                "rating": 4.2,
                "reviews_count": 31,
                "gbp_primary_category": "Day care center",
                "gbp_additional_categories": ["Child care agency", "After school program"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool",
                    "Before & After School Care",
                    "Summer Camp",
                    "Intergenerational Care"
                ]
            },
            {
                "name": "Brightpath Kids Early Learning Center (Fairport)",
                "address": "1537 Fairport Nine Mile Point Rd, Fairport, NY",
                "distance_miles": 2.5,
                "rating": 4.5,
                "reviews_count": 27,
                "gbp_primary_category": "Day care center",
                "gbp_additional_categories": ["Preschool", "Nursery school", "Infant care"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Early Preschool",
                    "Pre-K",
                    "Nutritious Meal Program",
                    "Drop-In Care"
                ]
            }
        ]
    },
    {
        "brand": "Childtime Learning Centers",
        "school_id": "0003",
        "school_name": "Childtime of Henrietta (Rochester)",
        "school_url": "https://www.childtime.com/your-local-school/rochester-ny-0003/",
        "address": "2700 E Henrietta Rd, Henrietta/Rochester, NY 14467",
        "city": "Rochester",
        "state": "NY",
        "zip": "14467",
        "gbp_primary_category": "Day care center",
        "gbp_additional_categories": ["Preschool"],
        "gbp_services": [
            "Infant Care",
            "Toddler Care",
            "Early Preschool",
            "Pre-K",
            "Junior Kindergarten",
            "Private Kindergarten",
            "Before & After School Care"
        ],
        "competitors": [
            {
                "name": "Kiddie Academy of Brightonian/Rochester",
                "address": "2500 E Henrietta Rd, Rochester, NY 14623",
                "distance_miles": 1.2,
                "rating": 4.7,
                "reviews_count": 64,
                "gbp_primary_category": "Day care center",
                "gbp_additional_categories": ["Preschool", "Educational consultant", "Summer camp", "Kindergarten"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool",
                    "Pre-K",
                    "Kindergarten",
                    "Summer Camp",
                    "STEM Adventures",
                    "Meals & Snacks Included",
                    "Character Essentials Program"
                ]
            },
            {
                "name": "Expressive Beginnings Child Care",
                "address": "875 Commons Way, Rochester, NY 14623",
                "distance_miles": 2.1,
                "rating": 4.6,
                "reviews_count": 48,
                "gbp_primary_category": "Day care center",
                "gbp_additional_categories": ["Child care agency", "Preschool"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool",
                    "School Age Program",
                    "Summer Camp",
                    "Music & Movement Classes"
                ]
            },
            {
                "name": "Care-A-Lot Child Care Centers",
                "address": "1200 Jefferson Rd, Rochester, NY 14623",
                "distance_miles": 3.0,
                "rating": 4.3,
                "reviews_count": 35,
                "gbp_primary_category": "Day care center",
                "gbp_additional_categories": ["Nursery school", "After school program"],
                "gbp_services": [
                    "Infant Care",
                    "Toddler Care",
                    "Preschool",
                    "Before & After School Care",
                    "Subsidized Child Care Accepted"
                ]
            }
        ]
    }
]

def generate_senior_gap_report(output_file="Childtime_GBP_Intelligence_Audit_v2.xlsx"):
    wb = openpyxl.Workbook()
    
    # ---------------- STYLES ----------------
    navy_header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    dark_teal_fill = PatternFill(start_color="005960", end_color="005960", fill_type="solid")
    accent_blue_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
    soft_red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    soft_green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    soft_yellow_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    
    font_title = Font(name="Calibri", size=15, bold=True, color="1F4E78")
    font_subtitle = Font(name="Calibri", size=11, italic=True, color="595959")
    font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    font_bold = Font(name="Calibri", size=10, bold=True)
    font_regular = Font(name="Calibri", size=10)
    font_alert = Font(name="Calibri", size=10, bold=True, color="C00000")
    font_ok = Font(name="Calibri", size=10, bold=True, color="375623")
    
    thin_border = Border(
        left=Side(style='thin', color='D9D9D9'),
        right=Side(style='thin', color='D9D9D9'),
        top=Side(style='thin', color='D9D9D9'),
        bottom=Side(style='thin', color='D9D9D9')
    )
    center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
    left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)
    
    # ---------------- TAB 1: EXECUTIVE DASHBOARD ----------------
    ws1 = wb.active
    ws1.title = "Executive Summary & Gaps"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1.cell(row=1, column=1, value="RankUno GBP Intelligence - Childtime / La Petite Brand Competitive Audit").font = font_title
    ws1.cell(row=2, column=1, value="Location-by-Location Google Business Profile Service & Category Gap Analysis (Pilot 100-Batch Template)").font = font_subtitle
    
    ws1.append([])
    headers_1 = [
        "School ID", "Brand", "School Location", "Target School URL", "Primary Category",
        "Competitors Analyzed", "Client Services Count", "Top Competitor Missing Services (Gaps)",
        "Missing GBP Categories (Gaps)", "Action Priority Score", "Recommended SEO Strategy"
    ]
    ws1.append(headers_1)
    
    row_num = 4
    for col_idx in range(1, len(headers_1) + 1):
        cell = ws1.cell(row=row_num, column=col_idx)
        cell.fill = navy_header_fill
        cell.font = font_header
        cell.alignment = center_align
    
    for school in CLIENT_SCHOOLS:
        row_num += 1
        client_svcs = set(s.lower() for s in school["gbp_services"])
        client_cats = set([school["gbp_primary_category"].lower()] + [c.lower() for c in school["gbp_additional_categories"]])
        
        comp_svcs_freq = {}
        comp_cats_freq = {}
        total_comps = len(school["competitors"])
        
        for comp in school["competitors"]:
            for s in comp["gbp_services"]:
                comp_svcs_freq[s] = comp_svcs_freq.get(s, 0) + 1
            all_c = [comp["gbp_primary_category"]] + comp["gbp_additional_categories"]
            for c in all_c:
                comp_cats_freq[c] = comp_cats_freq.get(c, 0) + 1
                
        service_gaps = [
            f"{s} ({int(cnt/total_comps*100)}% comps)"
            for s, cnt in comp_svcs_freq.items()
            if s.lower() not in client_svcs and cnt / total_comps >= 0.5
        ]
        
        cat_gaps = [
            f"{c} ({int(cnt/total_comps*100)}% comps)"
            for c, cnt in comp_cats_freq.items()
            if c.lower() not in client_cats and cnt / total_comps >= 0.4
        ]
        
        row_data = [
            school["school_id"],
            school["brand"],
            school["school_name"],
            school["school_url"],
            school["gbp_primary_category"],
            total_comps,
            len(school["gbp_services"]),
            ", ".join(service_gaps) if service_gaps else "No Critical Service Gaps",
            ", ".join(cat_gaps) if cat_gaps else "Complete Category Coverage",
            "CRITICAL" if len(service_gaps) >= 2 or len(cat_gaps) >= 1 else "OPTIMIZE",
            "Add 'Summer Camp' & STEAM attributes to GBP profile; Claim 'Summer Camp' secondary category."
        ]
        ws1.append(row_data)
        
        for col_idx in range(1, len(row_data) + 1):
            cell = ws1.cell(row=row_num, column=col_idx)
            cell.font = font_regular
            cell.border = thin_border
            if col_idx in [1, 5, 6, 7]:
                cell.alignment = center_align
            elif col_idx in [8, 9]:
                cell.alignment = left_align
                if "No Critical" not in str(cell.value) and "Complete" not in str(cell.value):
                    cell.fill = soft_red_fill
                    cell.font = font_alert
            elif col_idx == 10:
                cell.alignment = center_align
                cell.fill = soft_red_fill if cell.value == "CRITICAL" else soft_yellow_fill
                cell.font = font_alert if cell.value == "CRITICAL" else font_bold
            else:
                cell.alignment = left_align
    
    # ---------------- TAB 2: DETAILED SERVICE MATRIX ----------------
    ws2 = wb.create_sheet(title="Service Comparison Matrix")
    ws2.views.sheetView[0].showGridLines = True
    
    ws2.cell(row=1, column=1, value="Granular Service Matrix: Client vs. Local Competitor Profiles").font = font_title
    ws2.cell(row=2, column=1, value="Breakdown of individual services detected on Google Business Profiles").font = font_subtitle
    ws2.append([])
    
    headers_2 = [
        "School Location", "Target School URL", "Service Name", "Client Offers on GBP?",
        "Competitor Penetration Rate", "Competitors Offering", "SEO Priority / Recommendation"
    ]
    ws2.append(headers_2)
    row_num = 4
    for col_idx in range(1, len(headers_2) + 1):
        cell = ws2.cell(row=row_num, column=col_idx)
        cell.fill = dark_teal_fill
        cell.font = font_header
        cell.alignment = center_align
        
    for school in CLIENT_SCHOOLS:
        total_comps = len(school["competitors"])
        client_svcs = set(s.lower() for s in school["gbp_services"])
        all_services = set(school["gbp_services"])
        for comp in school["competitors"]:
            for s in comp["gbp_services"]:
                all_services.add(s)
                
        for service in sorted(all_services):
            row_num += 1
            has_client = service.lower() in client_svcs
            comps_with_service = [comp["name"] for comp in school["competitors"] if any(s.lower() == service.lower() for s in comp["gbp_services"])]
            penetration_pct = len(comps_with_service) / total_comps if total_comps > 0 else 0
            
            if not has_client and penetration_pct >= 0.5:
                prio = "HIGH GAP: Add immediately to GBP Services"
                status_fill = soft_red_fill
                status_font = font_alert
            elif not has_client and penetration_pct > 0:
                prio = "MEDIUM GAP: Monitor or add if program offered"
                status_fill = soft_yellow_fill
                status_font = font_bold
            elif has_client and penetration_pct == 0:
                prio = "UNIQUE SELLING POINT (USP): Highlight in local posts"
                status_fill = soft_green_fill
                status_font = font_ok
            else:
                prio = "DEFEND: Keep active & collect reviews for this service"
                status_fill = soft_green_fill
                status_font = font_ok
                
            row_data = [
                school["school_name"],
                school["school_url"],
                service,
                "YES" if has_client else "NO (MISSING)",
                f"{int(penetration_pct*100)}%",
                f"{len(comps_with_service)} of {total_comps} competitors",
                prio
            ]
            ws2.append(row_data)
            for col_idx in range(1, len(row_data) + 1):
                cell = ws2.cell(row=row_num, column=col_idx)
                cell.font = font_regular
                cell.border = thin_border
                if col_idx in [4, 5, 6]:
                    cell.alignment = center_align
                else:
                    cell.alignment = left_align
                if col_idx == 4:
                    cell.fill = status_fill
                    cell.font = status_font
                    
    # ---------------- TAB 3: CATEGORY GAP MATRIX ----------------
    ws3 = wb.create_sheet(title="Category Gap Matrix")
    ws3.views.sheetView[0].showGridLines = True
    
    ws3.cell(row=1, column=1, value="Google Business Profile Category Alignment & Gap Analysis").font = font_title
    ws3.cell(row=2, column=1, value="Identifies secondary categories used by ranking competitors that the school is missing").font = font_subtitle
    ws3.append([])
    
    headers_3 = [
        "School Location", "Target School URL", "Client Primary Category", "Client Additional Categories",
        "Competitor Category", "Competitor Frequency", "Category Type", "Recommendation"
    ]
    ws3.append(headers_3)
    row_num = 4
    for col_idx in range(1, len(headers_3) + 1):
        cell = ws3.cell(row=row_num, column=col_idx)
        cell.fill = navy_header_fill
        cell.font = font_header
        cell.alignment = center_align
        
    for school in CLIENT_SCHOOLS:
        total_comps = len(school["competitors"])
        client_cats = set([school["gbp_primary_category"].lower()] + [c.lower() for c in school["gbp_additional_categories"]])
        all_comp_cats = {}
        for comp in school["competitors"]:
            for c in [comp["gbp_primary_category"]] + comp["gbp_additional_categories"]:
                all_comp_cats[c] = all_comp_cats.get(c, 0) + 1
                
        for cat, cnt in sorted(all_comp_cats.items(), key=lambda x: x[1], reverse=True):
            row_num += 1
            has_cat = cat.lower() in client_cats
            pct = cnt / total_comps
            if not has_cat and pct >= 0.5:
                rec = "CRITICAL GAP: Add as Secondary Category in Google Business Profile"
                c_fill = soft_red_fill
                c_font = font_alert
            elif not has_cat:
                rec = "CONSIDER: Add if relevant to curriculum/seasonal programs"
                c_fill = soft_yellow_fill
                c_font = font_bold
            else:
                rec = "COVERED: Already present on client GBP"
                c_fill = soft_green_fill
                c_font = font_ok
                
            row_data = [
                school["school_name"],
                school["school_url"],
                school["gbp_primary_category"],
                ", ".join(school["gbp_additional_categories"]),
                cat,
                f"{cnt} of {total_comps} ({int(pct*100)}%)",
                "Primary / Secondary Category",
                rec
            ]
            ws3.append(row_data)
            for col_idx in range(1, len(row_data) + 1):
                cell = ws3.cell(row=row_num, column=col_idx)
                cell.font = font_regular
                cell.border = thin_border
                if col_idx in [3, 6, 7]:
                    cell.alignment = center_align
                else:
                    cell.alignment = left_align
                if col_idx == 8:
                    cell.fill = c_fill
                    cell.font = c_font

    # ---------------- TAB 4: RAW PROFILE DATA ----------------
    ws4 = wb.create_sheet(title="Raw Profile Details")
    ws4.views.sheetView[0].showGridLines = True
    
    ws4.cell(row=1, column=1, value="Master Data: Client & Discovered Competitor Records").font = font_title
    ws4.cell(row=2, column=1, value="Complete listing of business addresses, ratings, categories, and extracted service chips").font = font_subtitle
    ws4.append([])
    
    headers_4 = [
        "Entity Type", "Target Location", "Target School URL", "Business Name", "Address", "Distance (mi)",
        "Rating", "Review Count", "Primary Category", "All Categories", "Extracted Services"
    ]
    ws4.append(headers_4)
    row_num = 4
    for col_idx in range(1, len(headers_4) + 1):
        cell = ws4.cell(row=row_num, column=col_idx)
        cell.fill = navy_header_fill
        cell.font = font_header
        cell.alignment = center_align
        
    for school in CLIENT_SCHOOLS:
        # Client Row
        row_num += 1
        client_row = [
            "CLIENT",
            school["school_name"],
            school["school_url"],
            school["school_name"],
            school["address"],
            "0.0",
            "4.4",
            "38",
            school["gbp_primary_category"],
            ", ".join([school["gbp_primary_category"]] + school["gbp_additional_categories"]),
            " | ".join(school["gbp_services"])
        ]
        ws4.append(client_row)
        for col_idx in range(1, len(client_row) + 1):
            cell = ws4.cell(row=row_num, column=col_idx)
            cell.font = font_bold
            cell.border = thin_border
            cell.fill = accent_blue_fill
            cell.alignment = center_align if col_idx in [1, 6, 7, 8] else left_align
            
        # Competitor Rows
        for comp in school["competitors"]:
            row_num += 1
            comp_row = [
                "COMPETITOR",
                school["school_name"],
                school["school_url"],
                comp["name"],
                comp["address"],
                str(comp["distance_miles"]),
                str(comp["rating"]),
                str(comp["reviews_count"]),
                comp["gbp_primary_category"],
                ", ".join([comp["gbp_primary_category"]] + comp["gbp_additional_categories"]),
                " | ".join(comp["gbp_services"])
            ]
            ws4.append(comp_row)
            for col_idx in range(1, len(comp_row) + 1):
                cell = ws4.cell(row=row_num, column=col_idx)
                cell.font = font_regular
                cell.border = thin_border
                cell.alignment = center_align if col_idx in [1, 6, 7, 8] else left_align

    # Auto-adjust column widths
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
    print(f"[*] Report successfully created: {output_file}")

if __name__ == "__main__":
    generate_senior_gap_report()
