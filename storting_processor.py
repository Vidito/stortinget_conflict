import requests
import xml.etree.ElementTree as ET
import pandas as pd
from itertools import combinations
from collections import defaultdict
import time


class StortingDataProcessor:
    def __init__(self, session_id="2024-2025"):
        self.session_id = session_id
        self.base_url = "https://data.stortinget.no/eksport"
        self.ns = {"ns": "http://data.stortinget.no"}
        self.alliances = defaultdict(lambda: {"agree": 0, "disagree": 0})
        self.rebels = []
        self.controversial_votes = []
        self.representative_activity = defaultdict(
            lambda: {"total_votes": 0, "rebel_votes": 0}
        )
        self.topic_statistics = defaultdict(
            lambda: {
                "votes": 0,
                "total_for": 0,
                "total_against": 0,
                "controversy_sum": 0,
            }
        )
        self.party_voting_patterns = defaultdict(
            lambda: {"for_count": 0, "against_count": 0}
        )

    def _get_xml(self, endpoint, params=None):
        try:
            response = requests.get(f"{self.base_url}/{endpoint}", params=params)
            if response.status_code == 200:
                return ET.fromstring(response.content)
        except Exception as e:
            print(f"Error fetching {endpoint}: {e}")
        return None

    def get_party_votes(self, votering_id):
        """Processes individual votes to find the party majority and rebels."""
        res_xml = self._get_xml("voteringsresultat", {"voteringid": votering_id})
        if res_xml is None:
            return {}, []

        party_tallies = defaultdict(lambda: {"for": [], "mot": []})
        results = res_xml.findall(".//ns:representant_voteringsresultat", self.ns)

        for res in results:
            vote = res.find("ns:votering", self.ns).text
            if vote not in ["for", "mot"]:
                continue

            rep = res.find("ns:representant", self.ns)
            name = f"{rep.find('ns:fornavn', self.ns).text} {rep.find('ns:etternavn', self.ns).text}"
            party = rep.find("ns:parti/ns:id", self.ns).text
            party_tallies[party][vote].append(name)

            # Track representative activity
            self.representative_activity[name]["total_votes"] += 1

            # Track party voting patterns
            if vote == "for":
                self.party_voting_patterns[party]["for_count"] += 1
            else:
                self.party_voting_patterns[party]["against_count"] += 1

        party_lines = {}
        found_rebels = []

        for party, votes in party_tallies.items():
            f_count, m_count = len(votes["for"]), len(votes["mot"])
            majority = "for" if f_count > m_count else "mot"
            party_lines[party] = majority

            # Identify rebels
            rebel_vote = "mot" if majority == "for" else "for"
            for name in votes[rebel_vote]:
                found_rebels.append(
                    {
                        "Name": name,
                        "Party": party,
                        "Vote": rebel_vote,
                        "Majority": majority,
                        "Split": f"{len(votes[rebel_vote])} vs {max(f_count, m_count)}",
                    }
                )
                # Track rebel activity
                self.representative_activity[name]["rebel_votes"] += 1

        return party_lines, found_rebels

    def run_analysis(self, limit=50):
        """Main loop to fetch cases and process them."""
        saker_xml = self._get_xml("saker", {"sesjonid": self.session_id})
        if saker_xml is None:
            return

        saker = saker_xml.findall(".//ns:sak", self.ns)[:limit]

        for i, sak in enumerate(saker):
            sak_id = sak.find("ns:id", self.ns).text
            sak_tittel = sak.find("ns:tittel", self.ns).text
            print(f"Processing Case {i+1}/{limit}: {sak_id}", end="\r")

            v_xml = self._get_xml("voteringer", {"sakid": sak_id})
            if v_xml is None:
                continue

            for v in v_xml.findall(".//ns:sak_votering", self.ns):
                v_id = v.find("ns:votering_id", self.ns).text
                f_total = int(v.find("ns:antall_for", self.ns).text)
                m_total = int(v.find("ns:antall_mot", self.ns).text)
                topic = v.find("ns:votering_tema", self.ns).text

                # Calculate controversy score
                controversy_score = 0
                if (f_total + m_total) > 0:
                    controversy_score = 1 - abs(
                        (f_total - m_total) / (f_total + m_total)
                    )

                # 1. Analyze Party Alignment
                party_lines, rebels = self.get_party_votes(v_id)
                parties = sorted(list(party_lines.keys()))
                for p1, p2 in combinations(parties, 2):
                    if party_lines[p1] == party_lines[p2]:
                        self.alliances[(p1, p2)]["agree"] += 1
                    else:
                        self.alliances[(p1, p2)]["disagree"] += 1

                # 2. Store Rebels with Case Metadata
                for r in rebels:
                    r.update({"Case_ID": sak_id, "Title": sak_tittel, "Topic": topic})
                    self.rebels.append(r)

                # 3. Store Controversy Score
                self.controversial_votes.append(
                    {
                        "Case_ID": sak_id,
                        "Title": sak_tittel,
                        "Topic": topic,
                        "For": f_total,
                        "Against": m_total,
                        "Score": round(controversy_score, 3),
                    }
                )

                # 4. Track topic statistics
                self.topic_statistics[topic]["votes"] += 1
                self.topic_statistics[topic]["total_for"] += f_total
                self.topic_statistics[topic]["total_against"] += m_total
                self.topic_statistics[topic]["controversy_sum"] += controversy_score

        print(f"\nProcessing complete. Analyzed {len(saker)} cases.")

    def export_to_csv(self):
        """Saves processed data into CSV files for the dashboard."""
        # Export Rebels
        pd.DataFrame(self.rebels).to_csv("processed_rebels.csv", index=False)

        # Export Controversy
        pd.DataFrame(self.controversial_votes).to_csv(
            "processed_controversy.csv", index=False
        )

        # Export Alliance Matrix
        matrix_rows = []
        for (p1, p2), counts in self.alliances.items():
            total = counts["agree"] + counts["disagree"]
            rate = (counts["agree"] / total) * 100 if total > 0 else 0
            matrix_rows.append(
                {
                    "Party_A": p1,
                    "Party_B": p2,
                    "Agreement_Rate": round(rate, 1),
                    "Total_Votes": total,
                    "Agreements": counts["agree"],
                    "Disagreements": counts["disagree"],
                }
            )
        pd.DataFrame(matrix_rows).to_csv("processed_alliances.csv", index=False)

        # Export Representative Activity
        activity_rows = []
        for name, stats in self.representative_activity.items():
            rebel_rate = (
                (stats["rebel_votes"] / stats["total_votes"] * 100)
                if stats["total_votes"] > 0
                else 0
            )
            activity_rows.append(
                {
                    "Name": name,
                    "Total_Votes": stats["total_votes"],
                    "Rebel_Votes": stats["rebel_votes"],
                    "Rebel_Rate": round(rebel_rate, 1),
                }
            )
        pd.DataFrame(activity_rows).to_csv(
            "processed_representative_activity.csv", index=False
        )

        # Export Topic Statistics
        topic_rows = []
        for topic, stats in self.topic_statistics.items():
            avg_controversy = (
                stats["controversy_sum"] / stats["votes"] if stats["votes"] > 0 else 0
            )
            topic_rows.append(
                {
                    "Topic": topic,
                    "Total_Votes": stats["votes"],
                    "Total_For": stats["total_for"],
                    "Total_Against": stats["total_against"],
                    "Avg_Controversy": round(avg_controversy, 3),
                }
            )
        pd.DataFrame(topic_rows).to_csv("processed_topic_stats.csv", index=False)

        # Export Party Voting Patterns
        party_rows = []
        for party, stats in self.party_voting_patterns.items():
            total = stats["for_count"] + stats["against_count"]
            for_rate = (stats["for_count"] / total * 100) if total > 0 else 0
            party_rows.append(
                {
                    "Party": party,
                    "For_Count": stats["for_count"],
                    "Against_Count": stats["against_count"],
                    "For_Rate": round(for_rate, 1),
                }
            )
        pd.DataFrame(party_rows).to_csv("processed_party_patterns.csv", index=False)

        print("\n✅ All data exported successfully:")
        print("   - processed_rebels.csv")
        print("   - processed_controversy.csv")
        print("   - processed_alliances.csv")
        print("   - processed_representative_activity.csv")
        print("   - processed_topic_stats.csv")
        print("   - processed_party_patterns.csv")


if __name__ == "__main__":
    processor = StortingDataProcessor()
    processor.run_analysis(limit=50)
    processor.export_to_csv()
