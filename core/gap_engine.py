from typing import List, Dict, Any, Tuple
from core.normalizer import Normalizer

class GapEngine:
    def __init__(self):
        self.normalizer = Normalizer()

    def analyze_school(self, client_data: Dict[str, Any], competitors: List[Dict[str, Any]]) -> Dict[str, Any]:
        # 1. Filter out sister brands
        true_competitors = []
        sister_brands = []
        for comp in competitors:
            if self.normalizer.is_sister_brand(comp.get('name', ''), comp.get('website_url', '')):
                comp_copy = dict(comp)
                comp_copy['classification'] = 'SISTER BRAND (FILTERED)'
                sister_brands.append(comp_copy)
            else:
                comp_copy = dict(comp)
                comp_copy['classification'] = 'TRUE COMPETITOR'
                true_competitors.append(comp_copy)

        total_true = len(true_competitors)

        # 2. Internal Sync Gaps: Website programs vs GBP claimed services
        website_programs = [self.normalizer.normalize_service(p) for p in client_data.get('website_programs', [])]
        gbp_services = [self.normalizer.normalize_service(s) for s in client_data.get('gbp_services', [])]
        
        gbp_set = set(s.lower() for s in gbp_services)
        sync_gaps = []
        for prog in website_programs:
            if prog.lower() not in gbp_set:
                sync_gaps.append(prog)

        # 3. Competitor Service Adoption & Gaps
        comp_service_freq = {}
        for comp in true_competitors:
            for svc in comp.get('services', []):
                norm_svc = self.normalizer.normalize_service(svc)
                comp_service_freq[norm_svc] = comp_service_freq.get(norm_svc, 0) + 1

        ext_service_gaps = []
        service_matrix = []
        all_services = sorted(set(website_programs + gbp_services + list(comp_service_freq.keys())))

        for svc in all_services:
            has_website = any(svc.lower() == p.lower() for p in website_programs)
            has_gbp = any(svc.lower() == s.lower() for s in gbp_services)
            comp_count = comp_service_freq.get(svc, 0)
            adoption_pct = self.normalizer.calculate_rounded_percentage(comp_count, total_true)

            comps_offering = [
                c['name'] for c in true_competitors 
                if any(self.normalizer.normalize_service(s).lower() == svc.lower() for s in c.get('services', []))
            ]

            # Classification
            if has_website and not has_gbp and adoption_pct >= 50:
                finding = "CRITICAL SYNC GAP: School offers on site & competitors dominate Google, but Childtime GBP is missing chip!"
                ext_service_gaps.append(f"{svc} ({adoption_pct}%)")
            elif has_website and not has_gbp:
                finding = "INTERNAL SYNC GAP: School offers on website, but GBP dashboard has not published the service chip."
            elif has_gbp and adoption_pct >= 50:
                finding = "DEFEND: Active on GBP and competitive in market. Maintain review volume."
            elif has_gbp and adoption_pct == 0:
                finding = "DIFFERENTIATOR (USP): Childtime offers & highlights on GBP; competitors in territory omit."
            else:
                finding = "MONITOR: Niche offering in territory."

            service_matrix.append({
                'service_name': svc,
                'offered_website': 'YES' if has_website else 'NO',
                'claimed_gbp': 'YES' if has_gbp else 'NO (MISSING ON GBP)',
                'adoption_rate_pct': adoption_pct,
                'adoption_count': comp_count,
                'competitors_offering': comps_offering,
                'finding': finding
            })

        # 4. Category Gaps
        client_cats = set(
            [client_data.get('primary_category', '').lower()] + 
            [c.lower() for c in client_data.get('additional_categories', [])]
        )
        comp_cat_freq = {}
        for comp in true_competitors:
            all_c = [comp.get('primary_category', '')] + comp.get('additional_categories', [])
            for c in all_c:
                if c:
                    comp_cat_freq[c] = comp_cat_freq.get(c, 0) + 1

        category_gaps = []
        category_matrix = []
        for cat, count in sorted(comp_cat_freq.items(), key=lambda x: x[1], reverse=True):
            pct = self.normalizer.calculate_rounded_percentage(count, total_true)
            is_covered = cat.lower() in client_cats

            if not is_covered and pct >= 50:
                rec = "CRITICAL GAP: Add as Secondary Category on GBP to capture high-intent category search volume"
                category_gaps.append(f"{cat} ({pct}%)")
            elif not is_covered:
                rec = "CONSIDER: Add if relevant to curriculum or seasonal enrollment"
            else:
                rec = "COVERED: Currently active on Childtime GBP profile"

            category_matrix.append({
                'category_name': cat,
                'count': count,
                'pct': pct,
                'is_covered': is_covered,
                'recommendation': rec
            })

        return {
            'client_data': client_data,
            'true_competitors': true_competitors,
            'sister_brands': sister_brands,
            'sync_gaps': sync_gaps,
            'ext_service_gaps': ext_service_gaps,
            'category_gaps': category_gaps,
            'service_matrix': service_matrix,
            'category_matrix': category_matrix
        }

if __name__ == '__main__':
    engine = GapEngine()
    print("GapEngine initialized successfully.")
