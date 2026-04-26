from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend import schemas, crud, database, service  # Added service

router = APIRouter()

@router.post("/tickets", response_model=schemas.TicketResponse)
async def create_ticket(
    ticket: schemas.TicketCreate, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(database.get_db)
):
    db_ticket = crud.create_ticket_initial(db=db, ticket=ticket)
    background_tasks.add_task(service.analyze_ticket_service, db_ticket.id)
    return db_ticket