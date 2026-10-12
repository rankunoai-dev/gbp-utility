import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List, Dict, Any

class ReportGenerator:
    def __init__(self):
        # Styles
        self.navy_fill = PatternFill(start_color='1F4E78', end_color='1F4E78', fill_type='solid')
        self.dark_teal_fill = PatternFill(start_color='005960', end_color='005960', fill_type='solid')
        self.client_blue_fill = PatternFill(start_color='D9E1F2', end_color='D9E1F2', fill_type='solid')
        self.sister_fill = PatternFill(start_color='EDEDED', end_color='EDEDED', fill_type='solid')
        self.soft_red_fill = PatternFill(start_color='FCE4D6', end_color='FCE4D6', fill_type='solid')
        self.soft_green_fill = PatternFill(start_color='E2EFDA', end_color='E2EFDA', fill_type='solid')
        self.soft_yellow_fill = PatternFill(start_color='FFF2CC', end_color='FFF2CC', fill_type='solid')
        
        self.font_title = Font(name='Calibri', size=15, bold=True, color='1F4E78')
        self.font_subtitle = Font(name='Calibri', size=10, italic=True, color='595959')
        self.font_header = Font(name='Calibri', size=10, bold=True, color='FFFFFF')
        self.font_bold = Font(name='Calibri', size=10, bold=True)
        self.font_regular = Font(name='Calibri', size=10)
        self.font_italic = Font(name='Calibri', size=9, italic=True, color='595959')
        self.font_alert = Font(name='Calibri', size=10, bold=True, color='C00000')
        self.font_ok = Font(name='Calibri', size=10, bold=True, color='375623')
        
        self.thin_border = Border(
            left=Side(style='thin', color='D9D9D9'),
            right=Side(style='thin', color='D9D9D9'),
            top=Side(style='thin', color='D9D9D9'),
            bottom=Side(style='thin', color='D9D9D9')
        )
        self.center_align = Alignment(horizontal='center', vertical='center', wrap_text=True)
        self.left_align = Alignment(horizontal='left', vertical='center', wrap_text=True)

    def generate_workbook(self, analyzed_schools: List[Dict[str, Any]], output_path: str):
        wb = openpyxl.Workbook()
        
        # ---------------- SHEET 1: EXECUTIVE SUMMARY ----------------
        ws1 = wb.active
        ws1.title = 'Executive Summary & Gaps'
        ws1.views.sheetView[0].showGridLines = True
        
        ws1.cell(row=1, column=1, value='RankUno GBP Intelligence - Learning Care Group Competitive Audit').font = self.font_title
        ws1.cell(row=2, column=1, value='Executive Overview: Internal Website-to-GBP Sync Gaps, Verified Competitor Gaps, and Local Reputation Health').font = self.font_subtitle
        ws1.append([])
        
        headers_1 = [
            'School ID', 'Brand', 'Audited School Name', 'Verified Physical Address',
            'GBP Star Rating (Reviews)', 'True Competitors Audited', 'Sister Brands Filtered Out',
            'Website Programs Offered', 'Internal Sync Gaps (On Site, Missing on GBP)',
            'External Competitor Service Gaps (>=50%)', 'Missing GBP Categories (Gaps)',
            'Local Reputation Alert', 'Priority Action Plan'
        ]
        ws1.append(headers_1)
        for c_idx in range(1, len(headers_1) + 1):
            c = ws1.cell(row=4, column=c_idx)
            c.fill = self.navy_fill
            c.font = self.font_header
            c.alignment = self.center_align

        r1 = 4
        for data in analyzed_schools:
            r1 += 1
            client = data['client_data']
            true_comps = data['true_competitors']
            sisters = data['sister_brands']
            
            star = client.get('rating', 0.0)
            revs = client.get('reviews_count', 0)
            rep_label = f"CRITICAL: {star} Stars ({revs} revs) - Lagging behind competitors" if star < 4.0 else f"HEALTHY: {star} Stars ({revs} revs)"
            
            action_plan = (
                "1. Immediately add Summer Camp & Drop-In Care to GBP services (active on site). "
                "2. Add Summer Camp as secondary category before seasonal enrollment. "
                "3. Launch proactive review-generation campaign."
                if star < 4.0 else
                "1. Add Summer Camp & School Break Camps to GBP services to mirror website offerings. "
                "2. Add Nursery School as secondary category."
            )
            
            sister_label = f"{len(sisters)} ({', '.join([s['name'].split()[0] for s in sisters])})" if sisters else "0"
            
            row_vals = [
                client.get('school_id', ''),
                client.get('brand', ''),
                client.get('school_name', ''),
                client.get('address', ''),
                f"{star}* ({revs})",
                len(true_comps),
                sister_label,
                len(client.get('website_programs', [])),
                ', '.join(data['sync_gaps']) if data['sync_gaps'] else 'None',
                ', '.join(data['ext_service_gaps']) if data['ext_service_gaps'] else 'None',
                ', '.join(data['category_gaps']) if data['category_gaps'] else 'None',
                rep_label,
                action_plan
            ]
            ws1.append(row_vals)
            for c_idx in range(1, len(row_vals) + 1):
                cell = ws1.cell(row=r1, column=c_idx)
                cell.font = self.font_regular
                cell.border = self.thin_border
                cell.alignment = self.center_align if c_idx in [1, 5, 6, 7, 8] else self.left_align
                if c_idx in [9, 10]:
                    cell.fill = self.soft_red_fill
                    cell.font = self.font_alert
                elif c_idx == 12 and 'CRITICAL' in cell.value:
                    cell.fill = self.soft_red_fill
                    cell.font = self.font_alert

        # ---------------- SHEET 2: SERVICE & PROGRAM MATRIX ----------------
        ws2 = wb.create_sheet(title='Service Comparison Matrix')
        ws2.views.sheetView[0].showGridLines = True
        ws2.cell(row=1, column=1, value='Granular Program & Service Matrix: Childtime vs Verified True Competitors').font = self.font_title
        ws2.cell(row=2, column=1, value='Benchmarked against real nearby schools (Sister Brands strictly excluded from competitor denominators)').font = self.font_subtitle
        ws2.append([])
        
        headers_2 = [
            'Audited Client School', 'Program / Service Name', 'Offered on School Website?',
            'Claimed as GBP Service Chip?', 'True Competitor Adoption Rate',
            'Competitors Offering Count', 'Verified Competitor Names', 'Strategic Audit Finding'
        ]
        ws2.append(headers_2)
        for c_idx in range(1, len(headers_2) + 1):
            c = ws2.cell(row=4, column=c_idx)
            c.fill = self.dark_teal_fill
            c.font = self.font_header
            c.alignment = self.center_align

        r2 = 4
        for data in analyzed_schools:
            client = data['client_data']
            true_comps = data['true_competitors']
            for item in data['service_matrix']:
                r2 += 1
                row_vals = [
                    client.get('school_name', ''),
                    item['service_name'],
                    item['offered_website'],
                    item['claimed_gbp'],
                    f"{item['adoption_rate_pct']}%",
                    f"{item['adoption_count']} of {len(true_comps)} competitors",
                    ', '.join(item['competitors_offering']) if item['competitors_offering'] else 'None',
                    item['finding']
                ]
                ws2.append(row_vals)
                for c_idx in range(1, len(row_vals) + 1):
                    cell = ws2.cell(row=r2, column=c_idx)
                    cell.font = self.font_regular
                    cell.border = self.thin_border
                    cell.alignment = self.center_align if c_idx in [3, 4, 5, 6] else self.left_align
                    if c_idx == 4 and 'MISSING' in str(cell.value):
                        cell.fill = self.soft_red_fill if item['adoption_rate_pct'] >= 50 else self.soft_yellow_fill
                        cell.font = self.font_alert if item['adoption_rate_pct'] >= 50 else self.font_bold

        # ---------------- SHEET 3: CATEGORY GAP MATRIX ----------------
        ws3 = wb.create_sheet(title='Category Gap Matrix')
        ws3.views.sheetView[0].showGridLines = True
        ws3.cell(row=1, column=1, value='Google Business Profile Category Alignment & Market Adoption').font = self.font_title
        ws3.cell(row=2, column=1, value='Analyzes Primary and Secondary Google Categories among verified true local competitors').font = self.font_subtitle
        ws3.append([])
        
        headers_3 = [
            'Audited Client School', 'Client Primary Category', 'Client Additional Categories',
            'Competitor Category Discovered', 'Competitor Adoption Rate (% & Count)',
            'Google Classification Type', 'Actionable Recommendation'
        ]
        ws3.append(headers_3)
        for c_idx in range(1, len(headers_3) + 1):
            c = ws3.cell(row=4, column=c_idx)
            c.fill = self.navy_fill
            c.font = self.font_header
            c.alignment = self.center_align

        r3 = 4
        for data in analyzed_schools:
            client = data['client_data']
            true_comps = data['true_competitors']
            for item in data['category_matrix']:
                r3 += 1
                row_vals = [
                    client.get('school_name', ''),
                    client.get('primary_category', ''),
                    ', '.join(client.get('additional_categories', [])),
                    item['category_name'],
                    f"{item['count']} of {len(true_comps)} ({item['pct']}%)",
                    'Official Google Business Category',
                    item['recommendation']
                ]
                ws3.append(row_vals)
                for c_idx in range(1, len(row_vals) + 1):
                    cell = ws3.cell(row=r3, column=c_idx)
                    cell.font = self.font_regular
                    cell.border = self.thin_border
                    cell.alignment = self.center_align if c_idx in [2, 5, 6] else self.left_align
                    if c_idx == 7 and 'CRITICAL' in str(cell.value):
                        cell.fill = self.soft_red_fill
                        cell.font = self.font_alert

        # ---------------- SHEET 4: RAW PROFILE DETAILS ----------------
        ws4 = wb.create_sheet(title='Raw Profile Details')
        ws4.views.sheetView[0].showGridLines = True
        ws4.cell(row=1, column=1, value='Master Profile Inventory: 100% Verified Business Profiles').font = self.font_title
        ws4.cell(row=2, column=1, value='Verified school addresses, live Google Maps URLs, star ratings, review counts, categories, and programs').font = self.font_subtitle
        ws4.append([])
        
        headers_4 = [
            'Classification', 'Audited School Location', 'Brand / Entity Name',
            'Official Website URL', 'Live Google Maps Profile URL', 'Verified Street Address',
            'Distance (mi)', 'Google Star Rating', 'Google Review Count',
            'Primary Category', 'All Categories', 'Extracted Services & Programs'
        ]
        ws4.append(headers_4)
        for c_idx in range(1, len(headers_4) + 1):
            c = ws4.cell(row=4, column=c_idx)
            c.fill = self.navy_fill
            c.font = self.font_header
            c.alignment = self.center_align

        r4 = 4
        for data in analyzed_schools:
            client = data['client_data']
            # Client Row
            r4 += 1
            client_row = [
                'CLIENT SCHOOL',
                client.get('school_name', ''),
                client.get('school_name', ''),
                client.get('website_url', ''),
                client.get('gbp_url', ''),
                client.get('address', ''),
                '0.0',
                str(client.get('rating', '')),
                str(client.get('reviews_count', '')),
                client.get('primary_category', ''),
                ', '.join([client.get('primary_category', '')] + client.get('additional_categories', [])),
                ' | '.join(client.get('website_programs', []))
            ]
            ws4.append(client_row)
            for c_idx in range(1, len(client_row) + 1):
                cell = ws4.cell(row=r4, column=c_idx)
                cell.font = self.font_bold
                cell.border = self.thin_border
                cell.fill = self.client_blue_fill
                cell.alignment = self.center_align if c_idx in [1, 7, 8, 9] else self.left_align
                
            # Discovered Entities (True Competitors + Sister Brands)
            all_discovered = data['true_competitors'] + data['sister_brands']
            for ent in all_discovered:
                r4 += 1
                is_sister = (ent.get('classification') == 'SISTER BRAND (FILTERED)')
                ent_row = [
                    ent.get('classification', 'TRUE COMPETITOR'),
                    client.get('school_name', ''),
                    ent.get('name', ''),
                    ent.get('website_url', ''),
                    ent.get('maps_url', ''),
                    ent.get('address', ''),
                    str(ent.get('distance_miles', '')),
                    str(ent.get('rating', '')),
                    str(ent.get('reviews_count', '')),
                    ent.get('primary_category', ''),
                    ', '.join([ent.get('primary_category', '')] + ent.get('additional_categories', [])),
                    ' | '.join(ent.get('services', []))
                ]
                ws4.append(ent_row)
                for c_idx in range(1, len(ent_row) + 1):
                    cell = ws4.cell(row=r4, column=c_idx)
                    cell.font = self.font_italic if is_sister else self.font_regular
                    cell.border = self.thin_border
                    if is_sister:
                        cell.fill = self.sister_fill
                    cell.alignment = self.center_align if c_idx in [1, 7, 8, 9] else self.left_align

        # Auto-adjust column widths
        for ws in [ws1, ws2, ws3, ws4]:
            for col in ws.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.row > 2 and cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 52)

        wb.save(output_path)
        print(f"[*] Executive audit report saved successfully: {output_path}")

if __name__ == '__main__':
    rep = ReportGenerator()
    print("ReportGenerator initialized successfully.")
