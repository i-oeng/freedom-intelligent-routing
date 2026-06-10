import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from sqlalchemy import text
import time

geolocator = Nominatim(user_agent="freedom_routing_engine")
geo_cache = {}

def get_coordinates(address_string):
    """Base geocoding function with caching."""
    if not address_string or str(address_string).lower() == 'nan':
        return None
    if address_string in geo_cache:
        return geo_cache[address_string]
    try:

        time.sleep(0.1) 
        location = geolocator.geocode(address_string, timeout=5)
        if location:
            coords = (location.latitude, location.longitude)
            geo_cache[address_string] = coords
            return coords
    except Exception:
        pass
    return None

def get_robust_coords(city, street=None):
    """Attempts full address, falls back to city-only for maximum reliability."""
    if pd.isna(city) or not city:
        return None
        

    if pd.notna(street) and str(street).strip():
        coords = get_coordinates(f"{city}, {street}, Казахстан")
        if coords: return coords
        

    return get_coordinates(f"{city}, Казахстан")

def apply_skills(df, ticket, ai_data):
    """Filters a dataframe of managers by the strict hard skills."""
    res = df.copy()
    if ticket['segment'] in ['VIP', 'Priority']:
        res = res[res['skills'].str.contains('VIP', na=False)]
    if ai_data['ticket_type'] == 'Смена данных':
        res = res[res['role'].str.contains('Главный специалист|Глав спец', na=False, regex=True)]
    if ai_data['language'] in ['KZ', 'ENG']:
        res = res[res['skills'].str.contains(ai_data['language'], na=False)]
    return res

def route_ticket(ticket_id, engine, ai_data):
    ticket_id = int(ticket_id)
    with engine.connect() as conn:
        ticket = conn.execute(
            text("SELECT * FROM tickets WHERE id = :ticket_id"),
            {"ticket_id": ticket_id},
        ).mappings().fetchone()
        managers_df = pd.read_sql("SELECT * FROM managers", con=engine)
        offices_df = pd.read_sql("SELECT * FROM business_units", con=engine)

    if ticket is None:
        raise ValueError(f"Ticket {ticket_id} not found.")

    target_office = None
    eligible_managers = pd.DataFrame()

    if ticket['country'] != 'Казахстан' or pd.isna(ticket['city']):
        hub = 'Астана' if ticket_id % 2 == 0 else 'Алматы'
        hub_managers = managers_df[managers_df['unit_name'].str.contains(hub, na=False, case=False)]
        eligible_managers = apply_skills(hub_managers, ticket, ai_data)
        target_office = hub
        
        if eligible_managers.empty:
            other_hub = 'Алматы' if hub == 'Астана' else 'Астана'
            other_hub_managers = managers_df[managers_df['unit_name'].str.contains(other_hub, na=False, case=False)]
            eligible_managers = apply_skills(other_hub_managers, ticket, ai_data)
            target_office = other_hub
            

    else:

        client_coords = get_robust_coords(ticket['city'], ticket['street'])

        if not client_coords:

            target_office = 'Астана' if ticket_id % 2 == 0 else 'Алматы'
            eligible_managers = apply_skills(managers_df[managers_df['unit_name'].str.contains(target_office, case=False, na=False)], ticket, ai_data)
        else:
            distances = []
            for _, office in offices_df.iterrows():

                office_coords = get_robust_coords(office['office_name'])
                if office_coords:
                    dist = geodesic(client_coords, office_coords).kilometers
                    distances.append((office['office_name'], dist))
            
            distances.sort(key=lambda x: x[1])

            for office_name, dist in distances:
                local_managers = managers_df[managers_df['unit_name'].str.contains(office_name, na=False, case=False)]
                skilled_managers = apply_skills(local_managers, ticket, ai_data)
                
                if not skilled_managers.empty:
                    eligible_managers = skilled_managers
                    target_office = office_name
                    break 


    if eligible_managers.empty:
         eligible_managers = apply_skills(managers_df, ticket, ai_data)
         target_office = "Глобальный поиск"
         if eligible_managers.empty: 
             eligible_managers = managers_df.copy()


    eligible_managers = eligible_managers.sort_values(by=['current_load', 'id'])
    min_load = eligible_managers['current_load'].min()
    least_loaded = eligible_managers[eligible_managers['current_load'] == min_load].sort_values(by='id')
    chosen_index = ticket_id % len(least_loaded)
    chosen_manager = least_loaded.iloc[chosen_index]

    chosen_manager_id = int(chosen_manager['id'])


    with engine.begin() as conn:
        conn.execute(text("""
            UPDATE managers 
            SET "current_load" = "current_load" + 1 
            WHERE id = :manager_id
        """), {"manager_id": chosen_manager_id})
        
    return chosen_manager['full_name'], target_office, chosen_manager_id
