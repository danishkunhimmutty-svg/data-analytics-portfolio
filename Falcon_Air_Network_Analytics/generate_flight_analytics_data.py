"""
================================================================================
 FALCON AIR NETWORK ANALYTICS - SYNTHETIC DATA GENERATOR
================================================================================
Generates a realistic, relationally-consistent synthetic dataset for a
Flight Operations + Commercial Route Profitability Power BI model.

Outputs 6 CSV files matching the star schema:
    Dim_Date.csv
    Dim_Route.csv
    Dim_Aircraft.csv
    Dim_DelayCodes.csv
    Fact_Flights.csv
    Fact_RouteFinancials.csv

Requirements: pandas, numpy  (pip install pandas numpy)
Run:          python generate_flight_analytics_data.py
================================================================================
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

# ------------------------------------------------------------------------
# 0. CONFIG
# ------------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)

OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)
TARGET_FLIGHT_ROWS = 1600          # comfortably above the 1,500 minimum

HUBS = ["AUH", "DXB", "DOH", "RUH"]

HUB_NAMES = {
    "AUH": "Abu Dhabi Intl",
    "DXB": "Dubai Intl",
    "DOH": "Hamad Intl",
    "RUH": "King Khalid Intl",
}

# 25 Origin(Hub)-Destination(Spoke) route pairs, with realistic great-circle
# distances (km, approximate) and a route "type" classification.
ROUTES = [
    # RouteID          Origin  Dest   DestName                 DistanceKM
    ("AUH-LHR", "AUH", "LHR", "London Heathrow",        5710, "International", "Long Haul"),
    ("AUH-JFK", "AUH", "JFK", "New York JFK",           11690, "International", "Ultra Long Haul"),
    ("AUH-BOM", "AUH", "BOM", "Mumbai Chhatrapati",      1950, "Regional",       "Medium Haul"),
    ("AUH-DEL", "AUH", "DEL", "Delhi Indira Gandhi",     2190, "Regional",       "Medium Haul"),
    ("AUH-COK", "AUH", "COK", "Kochi Intl",              2620, "Regional",       "Medium Haul"),
    ("AUH-BKK", "AUH", "BKK", "Bangkok Suvarnabhumi",    5000, "International", "Long Haul"),
    ("AUH-MNL", "AUH", "MNL", "Manila Ninoy Aquino",     7770, "International", "Long Haul"),
    ("AUH-CAI", "AUH", "CAI", "Cairo Intl",              2410, "Regional",       "Medium Haul"),
    ("DXB-LHR", "DXB", "LHR", "London Heathrow",         5500, "International", "Long Haul"),
    ("DXB-JFK", "DXB", "JFK", "New York JFK",           11000, "International", "Ultra Long Haul"),
    ("DXB-CDG", "DXB", "CDG", "Paris Charles de Gaulle", 5240, "International", "Long Haul"),
    ("DXB-BOM", "DXB", "BOM", "Mumbai Chhatrapati",      1930, "Regional",       "Medium Haul"),
    ("DXB-SIN", "DXB", "SIN", "Singapore Changi",        5850, "International", "Long Haul"),
    ("DXB-HKG", "DXB", "HKG", "Hong Kong Intl",          5990, "International", "Long Haul"),
    ("DXB-IST", "DXB", "IST", "Istanbul Airport",        3000, "Regional",       "Medium Haul"),
    ("DOH-LHR", "DOH", "LHR", "London Heathrow",         5240, "International", "Long Haul"),
    ("DOH-FRA", "DOH", "FRA", "Frankfurt Main",          4680, "International", "Long Haul"),
    ("DOH-BOM", "DOH", "BOM", "Mumbai Chhatrapati",      1900, "Regional",       "Medium Haul"),
    ("DOH-KHI", "DOH", "KHI", "Karachi Jinnah",          1330, "Regional",       "Short Haul"),
    ("DOH-BKK", "DOH", "BKK", "Bangkok Suvarnabhumi",    4880, "International", "Long Haul"),
    ("DOH-CAI", "DOH", "CAI", "Cairo Intl",              2110, "Regional",       "Medium Haul"),
    ("RUH-CAI", "RUH", "CAI", "Cairo Intl",              1480, "Regional",       "Short Haul"),
    ("RUH-IST", "RUH", "IST", "Istanbul Airport",        2600, "Regional",       "Medium Haul"),
    ("RUH-BOM", "RUH", "BOM", "Mumbai Chhatrapati",      2530, "Regional",       "Medium Haul"),
    ("RUH-LHR", "RUH", "LHR", "London Heathrow",         5140, "International", "Long Haul"),
]

# Aircraft type performance/economics profile
AIRCRAFT_TYPES = {
    "A320":      {"seats": 180, "cruise_kmh": 828, "fuel_kg_per_hr": 2400, "range_km": 6300,  "cask_usd": 0.062},
    "B737-800":  {"seats": 189, "cruise_kmh": 842, "fuel_kg_per_hr": 2600, "range_km": 5400,  "cask_usd": 0.058},
    "B787-9":    {"seats": 296, "cruise_kmh": 903, "fuel_kg_per_hr": 5600, "range_km": 14140, "cask_usd": 0.045},
}

# Assign an aircraft type to each route based on distance / haul length
def assign_aircraft_type(distance_km):
    if distance_km >= 4500:
        return "B787-9"
    elif distance_km >= 2200:
        return np.random.choice(["B787-9", "B737-800"], p=[0.35, 0.65])
    else:
        return np.random.choice(["A320", "B737-800"], p=[0.55, 0.45])

# Delay root-cause taxonomy
DELAY_CODES = [
    ("DEL00", "No Delay",       "On-time or within buffer - no delay code applied", False),
    ("ATC01", "ATC",            "Air Traffic Control flow restriction / routing delay", False),
    ("ATC02", "ATC",            "Airspace / slot congestion at destination",            False),
    ("CXR01", "Carrier",        "Late crew report / crew scheduling",                   True),
    ("CXR02", "Carrier",        "Aircraft technical / maintenance hold",                True),
    ("CXR03", "Carrier",        "Cabin readiness / catering delay",                     True),
    ("WX01",  "Weather",        "Departure station adverse weather",                    False),
    ("WX02",  "Weather",        "Destination / enroute weather diversion risk",         False),
    ("RCT01", "Reactionary",    "Late inbound aircraft rotation",                       True),
    ("RCT02", "Reactionary",    "Late connecting passengers / baggage",                 True),
]

# ------------------------------------------------------------------------
# 1. DIM_DATE
# ------------------------------------------------------------------------
def build_dim_date(start, end):
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"Date": dates})
    df["DateKey"] = df["Date"].dt.strftime("%Y%m%d").astype(int)
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["MonthName"] = df["Date"].dt.strftime("%B")
    df["MonthSortIndex"] = df["Year"] * 100 + df["Month"]
    df["Quarter"] = "Q" + df["Date"].dt.quarter.astype(str)
    # Fiscal year assumed to start April 1 (common airline FY convention)
    fiscal_month = ((df["Month"] - 4) % 12) + 1
    df["FiscalQuarter"] = "FQ" + (((fiscal_month - 1) // 3) + 1).astype(str)
    df["FiscalYear"] = np.where(df["Month"] >= 4, df["Year"], df["Year"] - 1) + 1
    df["WeekNumber"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"] = df["Date"].dt.dayofweek + 1  # 1=Mon ... 7=Sun
    df["DayName"] = df["Date"].dt.strftime("%A")
    df["IsWeekend"] = df["DayOfWeek"].isin([6, 7])
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    cols = ["DateKey", "Date", "Year", "Quarter", "FiscalQuarter", "FiscalYear",
            "Month", "MonthName", "MonthSortIndex", "WeekNumber",
            "DayOfWeek", "DayName", "IsWeekend"]
    return df[cols]

dim_date = build_dim_date(START_DATE, END_DATE)

# Seasonal demand index per month (peak: Dec/Jan/Jul/Aug, trough: Feb/Sep)
SEASONAL_INDEX = {
    1: 1.18, 2: 0.90, 3: 0.95, 4: 1.00, 5: 0.98, 6: 1.05,
    7: 1.20, 8: 1.15, 9: 0.88, 10: 0.97, 11: 1.02, 12: 1.22,
}

# ------------------------------------------------------------------------
# 2. DIM_ROUTE
# ------------------------------------------------------------------------
route_rows = []
for i, (route_id, origin, dest, dest_name, dist, route_class, haul) in enumerate(ROUTES, start=1):
    ac_type = assign_aircraft_type(dist)
    route_rows.append({
        "RouteKey": i,
        "RouteID": route_id,
        "OriginAirportCode": origin,
        "OriginAirportName": HUB_NAMES[origin],
        "HubAirport": origin,
        "DestinationAirportCode": dest,
        "DestinationAirportName": dest_name,
        "RouteType": route_class,
        "HaulCategory": haul,
        "DistanceKM": dist,
        "PrimaryAircraftType": ac_type,
    })
dim_route = pd.DataFrame(route_rows)

# ------------------------------------------------------------------------
# 3. DIM_AIRCRAFT  (individual tails, 6 per type = 18 aircraft)
# ------------------------------------------------------------------------
aircraft_rows = []
key = 1
for ac_type, spec in AIRCRAFT_TYPES.items():
    n_tails = 6
    for t in range(1, n_tails + 1):
        aircraft_rows.append({
            "AircraftKey": key,
            "TailNumber": f"A6-{ac_type[:2].upper()}{t:02d}" if ac_type != "B787-9" else f"A6-BL{t:02d}",
            "AircraftType": ac_type,
            "Manufacturer": "Airbus" if ac_type == "A320" else "Boeing",
            "SeatCapacity": spec["seats"],
            "CruiseSpeedKMH": spec["cruise_kmh"],
            "FuelBurnRateKGPerHr": spec["fuel_kg_per_hr"],
            "RangeKM": spec["range_km"],
            "BaseCASK_USD": spec["cask_usd"],
        })
        key += 1
dim_aircraft = pd.DataFrame(aircraft_rows)

# ------------------------------------------------------------------------
# 4. DIM_DELAYCODES
# ------------------------------------------------------------------------
delay_rows = []
for i, (code, category, desc, controllable) in enumerate(DELAY_CODES, start=1):
    delay_rows.append({
        "DelayCodeKey": i,
        "DelayCode": code,
        "DelayCategory": category,
        "DelayDescription": desc,
        "IsCarrierControllable": controllable,
    })
dim_delaycodes = pd.DataFrame(delay_rows)
NO_DELAY_KEY = dim_delaycodes.loc[dim_delaycodes["DelayCategory"] == "No Delay", "DelayCodeKey"].iloc[0]
DELAY_KEY_BY_CATEGORY = {
    "ATC": dim_delaycodes[dim_delaycodes["DelayCategory"] == "ATC"]["DelayCodeKey"].tolist(),
    "Carrier": dim_delaycodes[dim_delaycodes["DelayCategory"] == "Carrier"]["DelayCodeKey"].tolist(),
    "Weather": dim_delaycodes[dim_delaycodes["DelayCategory"] == "Weather"]["DelayCodeKey"].tolist(),
    "Reactionary": dim_delaycodes[dim_delaycodes["DelayCategory"] == "Reactionary"]["DelayCodeKey"].tolist(),
}

# ------------------------------------------------------------------------
# 5. FACT_FLIGHTS
# ------------------------------------------------------------------------
# We simulate, per calendar day, a subset of routes operating, then generate
# flight legs with realistic OTP behaviour, seasonal load factors, and
# reactionary delay cascades driven by the previous sector flown by the
# same tail number that day.

dim_route_idx = dim_route.set_index("RouteKey")
dim_aircraft_by_type = {t: dim_aircraft[dim_aircraft["AircraftType"] == t] for t in AIRCRAFT_TYPES}

all_dates = pd.date_range(START_DATE, END_DATE, freq="D")
flight_rows = []
flight_id_counter = 100001

# Rough daily flight quota per route, scaled by season, to land close to
# TARGET_FLIGHT_ROWS across the full year without overshooting badly.
n_days = len(all_dates)
n_routes = len(dim_route)
base_flights_per_route_per_week = TARGET_FLIGHT_ROWS / n_routes / (n_days / 7)

# Track each tail's last actual arrival (for reactionary delay + turnaround)
tail_last_arrival = {t: None for t in dim_aircraft["TailNumber"]}
tail_last_route_dist = {t: None for t in dim_aircraft["TailNumber"]}

for date in all_dates:
    month = date.month
    season_factor = SEASONAL_INDEX[month]
    dow = date.dayofweek  # 0=Mon
    weekend_factor = 1.08 if dow in (4, 5) else 1.0  # Fri/Sat peak leisure travel

    for _, route in dim_route.iterrows():
        # Probability this route operates today (roughly daily, some thin
        # long-haul routes operate 4-5x/week)
        op_prob = 0.98 if route["HaulCategory"] != "Ultra Long Haul" else 0.72
        if np.random.random() > op_prob:
            continue

        # 1-2 flights/day on this route depending on haul length
        n_daily_flights = 1 if route["HaulCategory"] in ("Long Haul", "Ultra Long Haul") else np.random.choice([1, 2], p=[0.55, 0.45])

        ac_type = route["PrimaryAircraftType"]
        spec = AIRCRAFT_TYPES[ac_type]
        candidate_tails = dim_aircraft_by_type[ac_type]["TailNumber"].tolist()

        for leg in range(n_daily_flights):
            tail = np.random.choice(candidate_tails)

            # ---- Scheduled times ----
            sched_hour = np.random.choice(range(5, 23))
            sched_dep = datetime(date.year, date.month, date.day, sched_hour, np.random.choice([0, 15, 30, 45]))
            block_minutes_sched = int(round((route["DistanceKM"] / spec["cruise_kmh"]) * 60 + 25))  # +25 min taxi/climb buffer
            sched_arr = sched_dep + timedelta(minutes=block_minutes_sched)

            # ---- Reactionary delay from prior rotation of same tail ----
            reactionary_minutes = 0
            scheduled_turnaround = 45 if ac_type != "B787-9" else 90
            actual_turnaround = scheduled_turnaround
            if tail_last_arrival[tail] is not None:
                gap_minutes = (sched_dep - tail_last_arrival[tail]).total_seconds() / 60
                if 0 < gap_minutes < (scheduled_turnaround + 90):
                    # Tight rotation -> risk of reactionary delay cascading
                    shortfall = max(0, scheduled_turnaround - gap_minutes)
                    if shortfall > 0 or np.random.random() < 0.22:
                        reactionary_minutes = int(max(0, np.random.normal(loc=shortfall + 8, scale=10)))
                    actual_turnaround = max(15, gap_minutes)

            # ---- Root-cause delay draw ----
            delay_roll = np.random.random()
            primary_delay_minutes = 0
            delay_code_key = NO_DELAY_KEY

            if reactionary_minutes >= 10:
                delay_code_key = np.random.choice(DELAY_KEY_BY_CATEGORY["Reactionary"])
                primary_delay_minutes = reactionary_minutes
            elif delay_roll < 0.10:  # ATC
                delay_code_key = np.random.choice(DELAY_KEY_BY_CATEGORY["ATC"])
                primary_delay_minutes = int(max(0, np.random.gamma(shape=2.0, scale=9)))
            elif delay_roll < 0.20:  # Carrier
                delay_code_key = np.random.choice(DELAY_KEY_BY_CATEGORY["Carrier"])
                primary_delay_minutes = int(max(0, np.random.gamma(shape=2.2, scale=11)))
            elif delay_roll < 0.27:  # Weather (more likely Jun-Sep sandstorm/monsoon season)
                weather_boost = 1.6 if month in (6, 7, 8, 9) else 1.0
                if np.random.random() < 0.6 * weather_boost:
                    delay_code_key = np.random.choice(DELAY_KEY_BY_CATEGORY["Weather"])
                    primary_delay_minutes = int(max(0, np.random.gamma(shape=2.5, scale=14)))
            else:
                # small residual on-time noise
                primary_delay_minutes = int(max(0, np.random.normal(loc=2, scale=4)))
                if primary_delay_minutes < 1:
                    primary_delay_minutes = 0
                    delay_code_key = NO_DELAY_KEY

            departure_delay = primary_delay_minutes
            # Some delay is recovered in the air; arrival delay usually <= departure delay
            recovery = int(max(0, np.random.normal(loc=departure_delay * 0.25, scale=4)))
            arrival_delay = max(0, departure_delay - recovery)

            actual_dep = sched_dep + timedelta(minutes=departure_delay)
            actual_block = block_minutes_sched + np.random.randint(-6, 10)
            actual_arr = actual_dep + timedelta(minutes=actual_block)
            # keep arrival_delay internally consistent with actual timestamps
            arrival_delay = int(max(0, (actual_arr - sched_arr).total_seconds() / 60))

            # ---- Cancellation (rare, weather/ATC driven) ----
            is_cancelled = np.random.random() < (0.006 if delay_code_key not in DELAY_KEY_BY_CATEGORY["Weather"] else 0.03)

            # ---- Load factor / passengers ----
            route_popularity = 1.0
            if route["RouteType"] == "International" and route["HaulCategory"] != "Ultra Long Haul":
                route_popularity = 1.05
            if route["HaulCategory"] == "Ultra Long Haul":
                route_popularity = 0.97

            base_lf = 0.74
            lf = base_lf * season_factor * weekend_factor * route_popularity
            lf += np.random.normal(0, 0.05)
            lf = float(np.clip(lf, 0.42, 0.98))

            seats = spec["seats"]
            pax = 0 if is_cancelled else int(round(seats * lf))

            # ---- Fuel burn plan vs actual ----
            planned_fuel = spec["fuel_kg_per_hr"] * (block_minutes_sched / 60)
            fuel_variance_pct = np.random.normal(loc=0.015, scale=0.05)  # avg +1.5% burn vs plan
            actual_fuel = 0 if is_cancelled else planned_fuel * (1 + fuel_variance_pct)

            cargo_kg = 0 if is_cancelled else int(max(0, np.random.normal(loc=1800 if ac_type == "B787-9" else 600, scale=300)))

            flight_rows.append({
                "FlightKey": flight_id_counter,
                "FlightID": f"FA{flight_id_counter}",
                "DateKey": int(date.strftime("%Y%m%d")),
                "RouteKey": int(route["RouteKey"]),
                "AircraftKey": int(dim_aircraft.loc[dim_aircraft["TailNumber"] == tail, "AircraftKey"].iloc[0]),
                "DelayCodeKey": int(delay_code_key),
                "ScheduledDepartureDateTime": sched_dep.strftime("%Y-%m-%d %H:%M:%S"),
                "ActualDepartureDateTime": actual_dep.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
                "ScheduledArrivalDateTime": sched_arr.strftime("%Y-%m-%d %H:%M:%S"),
                "ActualArrivalDateTime": actual_arr.strftime("%Y-%m-%d %H:%M:%S") if not is_cancelled else "",
                "ScheduledBlockMinutes": block_minutes_sched,
                "ActualBlockMinutes": actual_block if not is_cancelled else 0,
                "DepartureDelayMinutes": 0 if is_cancelled else departure_delay,
                "ArrivalDelayMinutes": 0 if is_cancelled else arrival_delay,
                "ReactionaryDelayMinutes": 0 if is_cancelled else reactionary_minutes,
                "ScheduledTurnaroundMinutes": scheduled_turnaround,
                "ActualTurnaroundMinutes": int(actual_turnaround) if not is_cancelled else 0,
                "SeatsAvailable": seats,
                "PassengersBoarded": pax,
                "CargoKG": cargo_kg,
                "FuelBurnPlannedKG": round(planned_fuel, 1),
                "FuelBurnActualKG": round(actual_fuel, 1) if not is_cancelled else 0,
                "FlightStatus": "Cancelled" if is_cancelled else "Completed",
                "IsCancelled": is_cancelled,
            })

            if not is_cancelled:
                tail_last_arrival[tail] = actual_arr
                tail_last_route_dist[tail] = route["DistanceKM"]

            flight_id_counter += 1

fact_flights = pd.DataFrame(flight_rows)

# ------------------------------------------------------------------------
# 6. FACT_ROUTEFINANCIALS  (monthly grain, per route)
# ------------------------------------------------------------------------
fin_rows = []
fin_key = 1
months = pd.period_range(START_DATE, END_DATE, freq="M")

# Route-level fare/cost economics anchor (USD), roughly distance-scaled
for _, route in dim_route.iterrows():
    ac_type = route["PrimaryAircraftType"]
    spec = AIRCRAFT_TYPES[ac_type]
    dist = route["DistanceKM"]
    base_fare = 0.085 * dist + np.random.normal(0, 15)          # avg one-way fare USD
    base_fare = max(base_fare, 60)

    for month_period in months:
        month_num = month_period.month
        season_factor = SEASONAL_INDEX[month_num]

        # Pull matching flights for this route+month from Fact_Flights to
        # derive ASK/RPK consistently with operational data
        month_key_prefix = int(f"{month_period.year}{month_num:02d}")
        route_month_flights = fact_flights[
            (fact_flights["RouteKey"] == route["RouteKey"]) &
            (fact_flights["DateKey"] // 100 == month_key_prefix) &
            (fact_flights["IsCancelled"] == False)
        ]

        n_flights = len(route_month_flights)
        if n_flights == 0:
            continue

        total_seats = route_month_flights["SeatsAvailable"].sum()
        total_pax = route_month_flights["PassengersBoarded"].sum()
        ask = total_seats * dist
        rpk = total_pax * dist

        yield_per_rpk = (base_fare / dist) * np.random.normal(1.0, 0.06)
        yield_per_rpk = max(yield_per_rpk, 0.02)
        passenger_revenue = rpk * yield_per_rpk
        ancillary_revenue = passenger_revenue * np.random.uniform(0.06, 0.14)
        cargo_revenue = route_month_flights["CargoKG"].sum() * np.random.uniform(0.35, 0.55)
        total_revenue = passenger_revenue + ancillary_revenue + cargo_revenue

        fuel_cost = route_month_flights["FuelBurnActualKG"].sum() * np.random.uniform(0.78, 0.95)  # USD/kg jet fuel proxy
        crew_cost = n_flights * (spec["seats"] * 9.5) * (dist / 1000) * np.random.uniform(0.9, 1.1)
        maintenance_cost = n_flights * dist * 2.0 * np.random.uniform(0.9, 1.15)
        airport_charges = n_flights * (4200 if route["RouteType"] == "International" else 2600) * np.random.uniform(0.9, 1.1)
        other_opex = ask * spec["cask_usd"] * np.random.uniform(0.34, 0.50)

        total_cost = fuel_cost + crew_cost + maintenance_cost + airport_charges + other_opex

        fin_rows.append({
            "RouteFinKey": fin_key,
            "DateKey": int(f"{month_period.year}{month_num:02d}01"),
            "RouteKey": int(route["RouteKey"]),
            "AircraftKey": int(dim_aircraft[dim_aircraft["AircraftType"] == ac_type]["AircraftKey"].iloc[0]),
            "FlightCount": n_flights,
            "ASK": round(ask, 0),
            "RPK": round(rpk, 0),
            "PassengerRevenueUSD": round(passenger_revenue, 2),
            "AncillaryRevenueUSD": round(ancillary_revenue, 2),
            "CargoRevenueUSD": round(cargo_revenue, 2),
            "TotalRevenueUSD": round(total_revenue, 2),
            "FuelCostUSD": round(fuel_cost, 2),
            "CrewCostUSD": round(crew_cost, 2),
            "MaintenanceCostUSD": round(maintenance_cost, 2),
            "AirportChargesUSD": round(airport_charges, 2),
            "OtherOperatingCostUSD": round(other_opex, 2),
            "TotalOperatingCostUSD": round(total_cost, 2),
        })
        fin_key += 1

fact_routefinancials = pd.DataFrame(fin_rows)

# ------------------------------------------------------------------------
# 7. EXPORT
# ------------------------------------------------------------------------
dim_date.to_csv(f"{OUTPUT_DIR}/Dim_Date.csv", index=False)
dim_route.to_csv(f"{OUTPUT_DIR}/Dim_Route.csv", index=False)
dim_aircraft.to_csv(f"{OUTPUT_DIR}/Dim_Aircraft.csv", index=False)
dim_delaycodes.to_csv(f"{OUTPUT_DIR}/Dim_DelayCodes.csv", index=False)
fact_flights.to_csv(f"{OUTPUT_DIR}/Fact_Flights.csv", index=False)
fact_routefinancials.to_csv(f"{OUTPUT_DIR}/Fact_RouteFinancials.csv", index=False)

print("Export complete.")
print(f"  Dim_Date:              {len(dim_date):,} rows")
print(f"  Dim_Route:             {len(dim_route):,} rows")
print(f"  Dim_Aircraft:          {len(dim_aircraft):,} rows")
print(f"  Dim_DelayCodes:        {len(dim_delaycodes):,} rows")
print(f"  Fact_Flights:          {len(fact_flights):,} rows")
print(f"  Fact_RouteFinancials:  {len(fact_routefinancials):,} rows")
print(f"  Overall OTP (<=15min): {(fact_flights.loc[~fact_flights['IsCancelled'],'DepartureDelayMinutes'] <= 15).mean() * 100:.1f}%")
print(f"  Cancellation rate:     {fact_flights['IsCancelled'].mean() * 100:.2f}%")
