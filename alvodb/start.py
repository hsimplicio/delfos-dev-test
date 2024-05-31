from . import crud, schemas, database, models

def init_tables(signals: list[str]):
    """
    Create both tables and populate signal table
    """

    # Create tables if they do not exist
    models.Base.metadata.create_all(bind=database.engine)

    # Populate signal table with the possible signals
    db = next(database.get_db())
    
    if "timestamp" in signals:
        signals.remove("timestamp")
    
    for signal in signals:
        db_signal = crud.read_signal(db, signal)
        if not db_signal:
            crud.create_signal(db, schemas.SignalCreate(name=signal))

if __name__ == "__main__":
    init_tables()
