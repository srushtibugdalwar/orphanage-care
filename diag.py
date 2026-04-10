from app import app, Child, HealthRecord

with app.app_context():
    print("--- CHILDREN ---")
    children = Child.query.all()
    for c in children:
        print(f"ID: {c.id}, Name: {c.name}")
    
    print("\n--- HEALTH RECORDS ---")
    records = HealthRecord.query.all()
    for r in records:
        print(f"ID: {r.id}, ChildID: {r.child_id}, Medicine: {r.medicine}, Done: {r.is_done}")
