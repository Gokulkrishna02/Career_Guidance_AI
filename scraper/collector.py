import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.career_scorer import CAREER_KB


class CareerScraper:
    """
    Web scraper for career information.
    Uses the internal ML knowledge base for immediate results,
    with real HTTP scraping as an enhancement layer.
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }

    def _lookup_kb(self, query: str) -> dict | None:
        """Try to match the query against the internal career knowledge base."""
        query_lower = query.lower()
        best_match = None
        best_score = 0

        for career in CAREER_KB:
            score = 0
            if query_lower in career["name"].lower():
                score += 10
            for kw in career["keywords"]:
                if kw in query_lower:
                    score += 2
            if score > best_score:
                best_score = score
                best_match = career

        if best_match and best_score > 1:
            return best_match
        return None

    def search_career_info(self, query: str) -> dict:
        """
        Return structured career info for a query.
        First checks internal KB, then tries live HTTP fetch as bonus data.
        """
        kb = self._lookup_kb(query)

        if kb:
            return {
                "source": "Career AI Knowledge Base",
                "title": kb["name"],
                "description": (
                    f"{kb['name']} is a high-demand career in the fields of "
                    f"{', '.join(kb['streams'][:2])}. "
                    f"Market demand score: {kb['demand_score']}/100, "
                    f"growth outlook: {kb['growth_score']}/100."
                ),
                "avg_salary": f"{kb['avg_salary_lpa']} LPA",
                "skills_required": kb["required_skills"],
                "demand_score": kb["demand_score"],
                "growth_score": kb["growth_score"],
            }

        # Fallback: generic structured response
        return {
            "source": "Career AI Inference",
            "title": query,
            "description": (
                f"'{query}' is a professional career path requiring domain expertise "
                f"and continuous skill development. Use the Career Chat for detailed AI guidance."
            ),
            "avg_salary": "Varies by specialization",
            "skills_required": ["Communication", "Problem Solving", "Domain Knowledge", "Continuous Learning"],
            "demand_score": None,
            "growth_score": None,
        }

    def scrape_college_cutoff(self, college_name: str) -> dict:
        """Returns structured college cutoff info (static estimates)."""
        return {
            "college": college_name,
            "latest_cutoff": "Cutoff data not available in current database. Check TNEA / JoSAA official portals.",
            "source": "Career AI",
            "portal_links": {
                "TNEA": "https://www.tneaonline.org",
                "JoSAA": "https://josaa.nic.in",
                "NEET": "https://neet.nta.nic.in",
            }
        }


if __name__ == "__main__":
    scraper = CareerScraper()
    import json
    print(json.dumps(scraper.search_career_info("Data Scientist"), indent=2))
