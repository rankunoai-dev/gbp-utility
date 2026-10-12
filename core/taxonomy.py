"""Canonical program taxonomy shared by every stage of the engine.

Every raw service string (client website program, client GBP service chip,
competitor service) is mapped onto ONE canonical program name before any
comparison or percentage is computed. This is what makes the four report
sheets agree with each other: they all read from the same mapping.
"""

# Canonical programs in display/priority order. The order is used when
# listing gaps in the Executive Summary and the client's programs in the
# Raw Profile Details sheet.
CORE_PROGRAMS: tuple[str, ...] = (
    "Infant Care",
    "Toddler Care",
    "Twos",
    "Early Preschool",
    "Preschool Program",
    "Pre-K",
    "Junior Kindergarten",
    "Private Kindergarten",
    "Before and After School",
    "School Break Camps",
    "Summer Camp",
    "Drop-In Care",
    "Grow Fit",
    "Electives",
)

# Lower-case raw label -> canonical program. Anything not listed here is an
# "unmapped" service: it stays visible in Raw Profile Details but is not
# benchmarked in the Service Comparison Matrix.
SERVICE_SYNONYMS: dict[str, str] = {
    # Infant Care
    "infant care": "Infant Care",
    "infants": "Infant Care",
    "infant": "Infant Care",
    "infant program": "Infant Care",
    # Toddler Care
    "toddler care": "Toddler Care",
    "toddlers": "Toddler Care",
    "toddler": "Toddler Care",
    "toddler program": "Toddler Care",
    # Twos
    "twos": "Twos",
    "two's": "Twos",
    "two year olds": "Twos",
    # Early Preschool
    "early preschool": "Early Preschool",
    "discovery preschool": "Early Preschool",
    # Preschool Program
    "preschool program": "Preschool Program",
    "preschool": "Preschool Program",
    "pre-school": "Preschool Program",
    # Pre-K
    "pre-k": "Pre-K",
    "prek": "Pre-K",
    "pre k": "Pre-K",
    "pre-kindergarten": "Pre-K",
    "pre kindergarten": "Pre-K",
    "pre-k readiness": "Pre-K",
    # Junior Kindergarten
    "junior kindergarten": "Junior Kindergarten",
    # Private Kindergarten (a competitor's plain "Kindergarten" chip is a
    # private kindergarten offered inside a child-care centre)
    "private kindergarten": "Private Kindergarten",
    "kindergarten": "Private Kindergarten",
    # Before and After School
    "before and after school": "Before and After School",
    "before and after school care": "Before and After School",
    "before/after school": "Before and After School",
    "before and after school program": "Before and After School",
    "school age": "Before and After School",
    "school-age": "Before and After School",
    # School Break Camps
    "school break camps": "School Break Camps",
    "school break camp": "School Break Camps",
    # Summer Camp
    "summer camp": "Summer Camp",
    "summer camps": "Summer Camp",
    "summer program": "Summer Camp",
    # Drop-In Care
    "drop-in care": "Drop-In Care",
    "drop in care": "Drop-In Care",
    # Grow Fit
    "grow fit": "Grow Fit",
    # Electives (Childtime markets these as enrichment classes)
    "electives": "Electives",
    "enrichment programs": "Electives",
    "enrichment program": "Electives",
    "enrichment arts and music": "Electives",
}
