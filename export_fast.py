import requests
import pandas as pd
import sys

# # # # IMPORTANT
# I am not well versed in the usage of APIs.
# While I wrote the rest of the code in this project, this file was written
# by Google Gemini (and made more efficient/usable by me).
# I do not know how much of this works, but it appears to.
# Alter at your own risk. I recommend leaving well alone.


# fetch() goes through the WCA Live API and saves a .csv of all the currently
# entered results for a competition. It then returns a string of the filename
# the data is stored at, so the other program(s) can find it.

# --- Configuration ---
def fetch(comp_id):
    WCA_LIVE_API_URL = "https://live.worldcubeassociation.org/api"

    HEADERS = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36",
        "Origin": "https://live.worldcubeassociation.org"
    }

    # 2. FETCH STRUCTURE
    structure_query = f"""
    {{
      competition(id: "{comp_id}") {{
        id
        name
        competitionEvents {{
          event {{ id name }}
          rounds {{ id name }}
        }}
      }}
    }}
    """

    data = requests.post(WCA_LIVE_API_URL, json={"query": structure_query}, headers=HEADERS).json().get("data")

    if not data or not data.get("competition"):
        print("[!] Error: Could not find competition. Check the numeric ID.")
        sys.exit()

    comp_name = data["competition"]["name"].replace(" ", "")
    events = data["competition"]["competitionEvents"]
    all_rows = []

    # 3. FETCH ROUNDS
    for event in events:
        event_id = event["event"]["id"]

        for round_info in event["rounds"]:
            r_id = round_info["id"]
            r_name = round_info["name"]

            round_query = f"""
            {{
              round(id: "{r_id}") {{
                results {{
                  ranking
                  person {{ name wcaId country {{ name }} }}
                  attempts {{ result }}
                  best
                  average
                }}
              }}
            }}
            """

            r_data = requests.post(WCA_LIVE_API_URL, json={"query": round_query}, headers=HEADERS).json().get("data")

            if not r_data or not r_data.get("round"):
                continue

            results = r_data["round"]["results"]

            for res in results:
                p = res["person"]

                row = {
                    "Event": event_id,
                    "Round": r_name,
                    "Rank": res["ranking"],
                    "Name": p["name"],
                    "WCA ID": p["wcaId"] or "",
                    "Country": p["country"]["name"],
                    "Newcomer": p["wcaId"] is None,  # I added this column but actually never ended up using it
                    # and all my column references were hardcoded so it would be hard to change at this point
                    "Best": res["best"],
                    "Average": res["average"]
                }

                for i, attempt in enumerate(res["attempts"]):
                    row[f"Solve {i+1}"] = attempt["result"]

                all_rows.append(row)

    # 4. EXPORT
    if all_rows:
        filename = f"{comp_name}_results.csv"
        df = pd.DataFrame(all_rows)

        base_cols = ["Event", "Round", "Rank", "Name", "WCA ID", "Country", "Newcomer", "Best", "Average"]
        solve_cols = sorted([c for c in df.columns if "Solve" in c])

        final_cols = [c for c in base_cols + solve_cols if c in df.columns]

        df[final_cols].to_csv(filename, index=False, encoding='utf-8-sig')  # utf encoding for multilingual names
        print(f"\nSUCCESS! Saved {len(df)} rows to: {filename}")
        return filename
