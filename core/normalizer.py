from typing import List, Dict, Any, Tuple

class Normalizer:
    def __init__(self, sister_brands: List[str] = None):
        self.sister_brands = sister_brands or [
            "childtime", "la petite academy", "tutor time", "the children's courtyard",
            "everbrook academy", "montessori unlimited", "creative kids", "pathways learning",
            "young school", "apple tree", "u-gro"
        ]
        
        # Taxonomy mapping: map competitor variations to standard service names
        self.service_synonyms = {
            "preschool program": "Preschool",
            "pre-kindergarten": "Pre-K",
            "discovery preschool": "Early Preschool",
            "school break camps": "School Break Camps",
            "summer camp": "Summer Camp",
            "summer program": "Summer Camp",
            "before & after school": "Before and After School",
            "before and after school": "Before and After School",
            "before & after school care": "Before and After School",
            "infant care": "Infants",
            "toddler care": "Toddlers",
            "toddler program": "Toddlers",
            "twos": "Twos",
            "drop-in care": "Drop-In Care",
            "grow fit": "Grow Fit",
            "private kindergarten": "Private Kindergarten",
            "junior kindergarten": "Junior Kindergarten"
        }

    def is_sister_brand(self, business_name: str, domain_or_url: str = "") -> bool:
        combined = f"{business_name.lower()} {domain_or_url.lower()}"
        return any(brand in combined for brand in self.sister_brands)

    def normalize_service(self, raw_service: str) -> str:
        clean = raw_service.strip().lower()
        return self.service_synonyms.get(clean, raw_service.strip())

    @staticmethod
    def calculate_rounded_percentage(count: int, total: int) -> int:
        if total == 0:
            return 0
        return round((count / total) * 100)

if __name__ == '__main__':
    norm = Normalizer()
    print("Is La Petite a sister brand?", norm.is_sister_brand("La Petite Academy of Victor", "lapetite.com"))
    print("Is Goddard a sister brand?", norm.is_sister_brand("The Goddard School", "goddardschool.com"))
    print("Rounding 2 of 3:", norm.calculate_rounded_percentage(2, 3), "%")
