from . import crud, schemas, database, models

def init_tables():
    # Create tables if they do not exist
    models.Base.metadata.create_all(bind=database.engine)

    # Populate signal table with the possible signals
    db = next(database.get_db())
    signals = ['power', 'wind_speed', 'ambient_temperature']
    for signal in signals:
        db_signal = crud.get_signal(db, signal)
        if not db_signal:
            crud.create_signal(db, schemas.SignalCreate(name=signal))

if __name__ == "__main__":
    models.Base.metadata.create_all(bind=database.engine)
    init_tables()
