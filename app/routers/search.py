from fastapi import APIRouter, Depends, HTTPException, status
from starlette.status import HTTP_200_OK

from ..schemas import search_schema
from ..db.database import create_connection
from sqlalchemy.orm import Session
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *

from ..db.init_db import engine
from ..security import auth

router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


@router.get("/", response_model=List[search_schema.GetSearch], status_code=HTTP_200_OK,
            summary="Looks up any profile.")
def get_search(db: Session = Depends(create_connection),
               search_string: Optional[str] = "",
               user: User = Depends(auth.get_current_user)):
    """
        Response values:

        - **name**: full name of professor, user or object
        - **code**: shortcut for name
        - **id**: unique identifier for given entity
    """

    #search_string = '%' + search_string + '%'
    con = engine.connect()
    rs = con.execute(text(f"""select * from (
                  select s.name as name, s.code as code, s.id
                  from subject_table s
                  union
                  select concat(p.first_name, ' ', p.last_name) as name, 'PROF' as code, p.id
                  from professor_table p
                  union
                  select concat(u.first_name, ' ', u.last_name) as name, 'USER' as code, u.id
                  from user_table u
              ) as search
                where lower(search.name) like lower('%{search_string}%') or lower(search.code) like lower('%{search_string}%');"""))
    data = rs.fetchall()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There was an error querying desired data."
        )
    return data

    """if search_string == '':
        pass
    else:

        sub = (select([Subject.name, Subject.code, Subject.id])).as_scalar()
        prof = (select([func.concat(Professor.first_name, ' ', Professor.last_name).label('name'),
                        text("PROF").label('code'), Professor.id])).as_scalar()
        user = (select([func.concat(User.first_name, ' ', User.last_name).label('name'),
                        alias(text("USER"), name='code'), User.id])).as_scalar()

        unioned = sub.union(prof).union(user)
        results = db.query(unioned).filter(or_(unioned.name.like(f'%{search_string}%'),
                                               unioned.code.like(f'%{search_string}%')))
        """
