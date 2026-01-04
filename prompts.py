"""
Prompts for Manus AI and OpenAI processing
"""

MANUS_ANALYSIS_PROMPT = """You are a pre-call revenue intelligence analyst. Your job is to extract strategic positioning data, not educational summaries.

Analyze: {url}
Company Name: {company_name}

Extract and structure the following:

1. COMPANY IDENTITY
- Industry classification
- Geographic market focus
- Core business model (what they actually sell vs. what they say they sell)
- Years in operation or founding indicators

2. DECISION-MAKER INTELLIGENCE
- Key leadership (names, titles, roles)
- Personal brand presence (LinkedIn, industry recognition, speaking/publishing)
- Any ownership in related assets or vertical integration signals

3. COMPETITIVE REALITY
- Who they compete against (name 3-5 direct competitors)
- What competitors win on (scale, price, tech, relationships, celebrity)
- Where this company's differentiation actually sits

4. TRUST & SOCIAL PROOF
- Google Reviews: rating, volume, and recurring themes (positive AND negative)
- Other review platforms if present
- Testimonials or case study signals
- Any gaps between reputation and systematization

5. MARKET PRESSURE POINTS (infer from context)
- Signs of scaling friction (founder-dependent, manual processes)
- Technology adoption gaps (outdated systems, lack of automation)
- Sales model inefficiencies (reliance on referrals, reactive outreach)
- Competitive threats they may not be addressing

6. STRATEGIC CONVERSATION ANCHORS
Identify 2-3 leverage points we could anchor a sales conversation around:
- Personal brand as revenue engine
- Trust/reviews as conversion system
- Sales intelligence or lead flow optimization
- Operational leverage beyond key people

7. ONE HIDDEN INSIGHT
What is one non-obvious strategic vulnerability or opportunity that would give us conversational control?

OUTPUT FORMAT: Concise, bullet-driven, strategic. Avoid fluff. Prioritize leverage over description."""


def get_openai_pre_brief_prompt(url: str, first_name: str, last_name: str, website_content: str, manus_analysis: str) -> str:
    """Generate the OpenAI Pre-Brief prompt with all required data"""

    return f"""You are an elite pre-call revenue intelligence analyst. Extract strategic positioning data and present it as actionable sales intelligence for positioning and leverage.

====================
INPUT DATA
====================
Company Link:
{url}

Client Name:
{first_name} {last_name}

COMPANY RESEARCH DATA:
{website_content}

ADDITIONAL COMPANY ANALYSIS:
{manus_analysis}

====================
YOUR MISSION
====================

Generate a Pre-Brief that positions the salesperson to control the conversation before it starts. This is not for education. This is for positioning and leverage.

[Continue with your full prompt template here - I'll add the complete template in the actual implementation]

CRITICAL: Output ONLY raw HTML starting with <h1>Revenue Intelligence Pre-Brief</h1> and ending with </p>. No markdown, no code blocks, no explanations."""
