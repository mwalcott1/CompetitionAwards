import requests
import pandas as pd
import sys

# # # # IMPORTANT
# I am not well versed in the usage of APIs.
# While I wrote the rest of the code in this project, this file was written
# by Google Gemini (and made more efficient/usable by me).
# I do not know how much of this works, but it appears to.
# Alter at your own risk. I recommend leaving well alone.


# fetchResults() goes through the WCA Live API and saves a .csv of all the currently
# entered results for a competition. It then returns a string of the filename
# the data is stored at, so the other program(s) can find it.

def fetchResults(comp_id):
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
        print("Competition not imported to Live, or no results entered yet.")
        return None

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




########################################################################



# fetchRegs does about the same thing as fetchResults, but goes through WCIF instead.
# as no results are entered, it makes a row with empty results for all events each person is registered for

def fetchRegs(comp_id):
    # 1. Fetch Country Mapping (to match WCA Live's full country names)
    countries_url = "https://www.worldcubeassociation.org/api/v0/countries"
    try:
        countries_data = requests.get(countries_url).json()
        # Build dictionary mapping iso2 (e.g., 'US') to Full Name (e.g., 'United States')
        iso2_to_name = {c.get("iso2"): c.get("name") for c in countries_data}
    except Exception:
        # Fallback empty dictionary if the countries endpoint fails
        iso2_to_name = {}

    # 2. Fetch Registration Data via Public WCIF
    wcif_url = f"https://www.worldcubeassociation.org/api/v0/competitions/{comp_id}/wcif/public"
    response = requests.get(wcif_url)
    
    if response.status_code != 200:
        print(f"[!] Error: Could not find competition. Check the numeric ID or URL string.")
        sys.exit()

    data = response.json()
    comp_name = data.get("name", comp_id).replace(" ", "")
    persons = data.get("persons", [])
    
    all_rows = []

    # 3. Process Registrations
    for person in persons:
        reg = person.get("registration")
        
        # Skip if they have no registration or if it hasn't been accepted yet
        if not reg or reg.get("status") != "accepted":
            continue

        name = person.get("name")
        wca_id = person.get("wcaId")
        country_iso2 = person.get("countryIso2")
        country_name = iso2_to_name.get(country_iso2, country_iso2) # fallback to code if name not found
        is_newcomer = (wca_id is None)

        # Create a row for every event this person is registered to compete in
        for event_id in reg.get("eventIds", []):
            row = {
                "Event": event_id,
                "Round": "",     # Left blank (results haven't happened yet)
                "Rank": "",      # Left blank
                "Name": name,
                "WCA ID": wca_id or "",
                "Country": country_name,
                "Newcomer": is_newcomer,
                "Best": "",      # Left blank
                "Average": ""    # Left blank
            }
            all_rows.append(row)

    # 4. Export
    if all_rows:
        filename = f"{comp_name}_WCIF_results.csv"
        df = pd.DataFrame(all_rows)

        # Enforce your exact hardcoded column structure 
        # (Solve columns are omitted here since they don't exist before the comp)
        base_cols = ["Event", "Round", "Rank", "Name", "WCA ID", "Country", "Newcomer", "Best", "Average"]
        
        df = df[base_cols]

        # utf-8-sig encoding ensures multilingual names render correctly in Excel
        df.to_csv(filename, index=False, encoding='utf-8-sig') 
        print(f"\nSUCCESS! Saved {len(df)} rows to: {filename}")
        return filename
    else:
        print("\nNo accepted registrations found for this competition.")
        return None