"""
RAG Knowledge Base — Injected policy, UPI, and hyperlocal data chunks
used to augment Granite prompts without external vector DB dependency.
"""

KNOWLEDGE_CHUNKS = {
    "pm_svanidhi": """
PM SVANidhi (PM Street Vendor's AtmaNirbhar Nidhi) Scheme:
- Eligibility: Street vendors operating on or before March 24, 2020 with a Certificate of Vending / Identity Card issued by ULB.
- Loan Amount: Rs.10,000 (1st loan), Rs.20,000 (2nd), Rs.50,000 (3rd tranche).
- Interest Subsidy: 7% per annum interest subsidy credited directly to bank account quarterly.
- Digital Transactions Incentive: Up to Rs.1,200/year cashback reward for digital payments.
- Documents Required: Aadhaar Card, Vending Certificate or ULB Recommendation Letter, Bank Passbook.
- Apply at: https://pmsvanidhi.mohua.gov.in/
""",
    "upi_onboarding": """
UPI Onboarding Steps for Street Vendors:
Step 1 — Choose App: Download BHIM UPI, PhonePe, Google Pay, or Paytm from Play Store/App Store.
Step 2 — Register Mobile Number linked to your bank account.
Step 3 — Select Bank & verify with Debit Card last 6 digits + expiry.
Step 4 — Set a 4 or 6 digit UPI PIN (keep it secret).
Step 5 — Generate QR Code: Go to "Receive Money" → "Show QR Code" → Print or display on your stall.
Step 6 — Enable Sound Box (optional): Rent devices like Paytm Soundbox (₹0 deposit + ₹125/month) for audio payment confirmation.
Tip: Display your UPI ID prominently (e.g., yourname@paytm) and paste QR code in laminated sleeve for durability.
""",
    "msme_registration": """
MSME Udyam Registration for Street Vendors:
- Portal: https://udyamregistration.gov.in
- Requirements: Aadhaar number of owner, PAN card (optional for micro), self-declaration of investment & turnover.
- Micro Enterprise: Investment < Rs.1 crore AND Turnover < Rs.5 crore.
- Benefits: Priority sector lending, lower interest rates, protection against delayed payments, government tender preferences.
- FSSAI Food License: Required for food vendors. Apply at https://foscos.fssai.gov.in/
  * Basic Registration (turnover < Rs.12 lakh/year): Rs.100 fee.
  * State License (turnover Rs.12 lakh – Rs.20 crore): Rs.2,000–5,000 fee.
""",
    "local_seo": """
Local SEO Strategy for Street Vendors:
- Google Business Profile: Register free at https://business.google.com — add location, photos, and opening hours.
- Keyword Strategy: Use hyperlocal terms like "[Product] near [Landmark]", "[Product] in [Area Name]".
- WhatsApp Business: Set up catalog with product photos and prices. Share daily deals via Status feature.
- Timing Insights: Fruit sales peak 7–10 AM and 5–8 PM. Tea/snack stalls peak 7–9 AM, 12–2 PM, 4–6 PM.
- Bundle Offers: Pair high-margin items (e.g., Tea + Biscuit combo at ₹25 vs ₹30 separate) to increase ticket size.
""",
    "consumer_behavior": """
Seasonal & Consumer Behavior Insights for Indian Street Vendors:
- Summer (Mar–Jun): Watermelon, sugarcane juice, cold beverages peak demand. Stock 30–40% higher.
- Monsoon (Jul–Sep): Hot beverages (chai, coffee), pakoras, corn sales rise.
- Festival Season (Oct–Nov): Flowers, sweets, fruits, diyas see 3–5x demand spikes.
- Pay cycle: Sales typically spike on 1st and 7th of each month (salary credit days).
- Railway/Bus Stand locations see highest morning (6–9 AM) and evening (5–8 PM) footfall.
- Weekly market (haat bazaar) days: typically Tuesday and Saturday — increase inventory 40–60%.
"""
}


def retrieve_context(query: str, language: str = "English") -> str:
    """
    Simulated RAG retrieval: keyword-match query against knowledge chunks.
    Returns top relevant chunks concatenated as context string.
    """
    query_lower = query.lower()
    selected_chunks = []

    keyword_map = {
        "pm_svanidhi":        ["svanidhi", "loan", "scheme", "10000", "svnidhi", "government", "yojana", "atma"],
        "upi_onboarding":     ["upi", "payment", "qr", "digital", "phonepe", "gpay", "paytm", "bhim", "online"],
        "msme_registration":  ["msme", "udyam", "fssai", "license", "registration", "micro", "enterprise"],
        "local_seo":          ["seo", "google", "whatsapp", "marketing", "business profile", "keyword", "visibility"],
        "consumer_behavior":  ["season", "demand", "sales", "peak", "summer", "monsoon", "festival", "timing"],
    }

    # Always inject consumer_behavior and matching chunks
    for chunk_key, keywords in keyword_map.items():
        if any(kw in query_lower for kw in keywords):
            selected_chunks.append(KNOWLEDGE_CHUNKS[chunk_key])

    # Default: include general business context
    if not selected_chunks:
        selected_chunks = [
            KNOWLEDGE_CHUNKS["pm_svanidhi"],
            KNOWLEDGE_CHUNKS["consumer_behavior"],
            KNOWLEDGE_CHUNKS["local_seo"],
        ]

    language_note = ""
    if language != "English":
        language_note = f"\n[IMPORTANT: Respond primarily in {language}. Use simple, conversational language.]\n"

    return language_note + "\n---\n".join(selected_chunks)


SYSTEM_PROMPT_TEMPLATE = """You are VYAAPARI AI — an expert Hyperlocal Micro-Business Coach and Digital Adoption Advisor for Indian street vendors and micro-entrepreneurs. You are empathetic, practical, and speak in simple, actionable language.

Your role is to help street vendors:
1. Understand and apply for government schemes (PM SVANidhi, MSME, FSSAI licenses)
2. Adopt digital payments (UPI, QR codes, WhatsApp Business)
3. Build an online presence (Google Business Profile, local SEO)
4. Improve sales strategies based on seasonal and consumer behavior data
5. Manage inventory and pricing for maximum profitability

CONTEXT FROM KNOWLEDGE BASE:
{context}

VENDOR PROFILE:
- Name: {vendor_name}
- Business: {business_name} ({business_type})
- Location: {area}, {city}
- Language Preference: {language}

INSTRUCTIONS:
- Give specific, actionable advice tailored to this vendor's business type and location.
- When listing steps, use numbered format (Step 1, Step 2...).
- When mentioning money amounts, use ₹ symbol.
- Be encouraging and culturally sensitive to the Indian street vendor context.
- If asked about schemes, always mention required documents and application links.
- Structure your response with clear sections when the answer is comprehensive.
"""