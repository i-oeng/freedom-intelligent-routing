import sys
import pandas as pd
import time

from config import DATA_DIR, MissingConfigError, get_engine


TICKET_COLUMNS = {
    "GUID клиента": "client_guid",
    "Пол клиента": "gender",
    "Дата рождения": "birth_date",
    "Сегмент клиента": "segment",
    "Описание": "description",
    "Вложения": "attachment",
    "Страна": "country",
    "Область": "region",
    "Населённый пункт": "city",
    "Улица": "street",
    "Дом": "building",
}


def load_csv_to_db(include_tickets: bool = False):
    engine = get_engine()
    print("Starting data ingestion...")
    start_time = time.time()

    print("Loading Business Units...")
    df_units = pd.read_csv(DATA_DIR / "business_units.csv")
    df_units.columns = df_units.columns.str.strip()
    df_units = df_units.rename(columns={
        "Офис": "office_name",
        "Адрес": "address"
    })
    df_units.to_sql("business_units", con=engine, if_exists="append", index=False)

 
    print("Loading Managers...")
    df_managers = pd.read_csv(DATA_DIR / "managers.csv")
    df_managers.columns = df_managers.columns.str.strip()
    df_managers = df_managers.rename(columns={
        "ФИО": "full_name",
        "Должность": "role", 
        "Навыки": "skills",
        "Офис": "unit_name", 
        "Количество обращений в работе": "current_load" 
    })
    df_managers.to_sql("managers", con=engine, if_exists="append", index=False)

    if include_tickets:
        print("Loading Tickets...")
        df_tickets = pd.read_csv(DATA_DIR / "tickets.csv")
        df_tickets.columns = df_tickets.columns.str.strip()
        df_tickets = df_tickets.rename(columns=TICKET_COLUMNS)
        df_tickets.to_sql("tickets", con=engine, if_exists="append", index=False)

    end_time = time.time()
    print(f"Data ingestion complete in {round(end_time - start_time, 2)} seconds!")

if __name__ == "__main__":
    try:
        load_csv_to_db(include_tickets="--include-tickets" in sys.argv)
    except MissingConfigError as exc:
        raise SystemExit(str(exc)) from exc
