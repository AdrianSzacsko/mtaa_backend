import json

from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK
from starlette.websockets import WebSocketDisconnect

from ..schemas import search_schema
from ..db.database import create_connection, async_create_connection
from sqlalchemy.orm import Session
from sqlalchemy import func, union, select, or_, alias, text
from typing import List, Optional
from ..models import *

from ..db.init_db import engine
from ..security import auth

router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={401: {"description": "Not authorized to perform this action."},
               404: {"description": "There was an error querying desired data."}}
)


@router.get("/", response_model=List[search_schema.GetSearch], status_code=HTTP_200_OK,
            summary="Looks up any profile.")
def get_search(db: Session = Depends(create_connection),
               search_string: Optional[str] = "",
               user: User = Depends(auth.get_current_user)):
    """
        Input parameters:
        - **search_string**: optional, defines keyword to search for

        Response values:

        - **name**: full name of professor, user or object
        - **code**: shortcut for name
        - **id**: unique identifier for given entity
    """

    # search_string = '%' + search_string + '%'
    con = engine.connect()
    rs = con.execute(text(f"""select name, code, id from (
                               select *,
                                      row_number() over (partition by pointer) as rn
                               from (
                                        select *
                                        from (
                                                 (select s.name as name, s.code as code, s.id, 'subj' as pointer
                                                  from subject_table s)
                                                 union
                                                 (select concat(p.first_name, ' ', p.last_name) as name,
                                                         'PROF'                                 as code,
                                                         p.id,
                                                         'prof'                                 as pointer
                                                  from professor_table p)
                                                 union
                                                 (select concat(u.first_name, ' ', u.last_name) as name,
                                                         'USER'                                 as code,
                                                         u.id,
                                                         'user'                                 as pointer
                                                  from user_table u)
                                             ) as search
                                        where case
                                                  when '{search_string}' = 'default_value'
                                                      then lower(search.code) like '%'
                                                  else lower(search.name) like lower('%{search_string}%') or
                                                       lower(search.code) like lower('%{search_string}%') end
                                    ) as tmp
                               order by rn, pointer
                           ) as tmp2;"""))  # direct sql select into database
    data = rs.fetchall()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"There was an error querying desired data."
        )
    return data


@router.websocket("/wb")
async def get_search_wb(websocket: WebSocket,
                        ):
    """
        - **name**: full name of professor, user or object
        - **code**: shortcut for name
        - **id**: unique identifier for given entity
    """

    await websocket.accept()
    token = websocket.headers["authorization"]
    db = await async_create_connection()
    user: User = await auth.async_get_current_user(token=token, db=db)
    if db:
        db.close()

    con = engine.connect()
    try:
        while True:
            search_string = await websocket.receive_text()
        # search_string = '%' + search_string + '%'
            rs = con.execute(text(f"""select name, code, id from (
                                       select *,
                                              row_number() over (partition by pointer) as rn
                                       from (
                                                select *
                                                from (
                                                         (select s.name as name, s.code as code, s.id, 'subj' as pointer
                                                          from subject_table s)
                                                         union
                                                         (select concat(p.first_name, ' ', p.last_name) as name,
                                                                 'PROF'                                 as code,
                                                                 p.id,
                                                                 'prof'                                 as pointer
                                                          from professor_table p)
                                                         union
                                                         (select concat(u.first_name, ' ', u.last_name) as name,
                                                                 'USER'                                 as code,
                                                                 u.id,
                                                                 'user'                                 as pointer
                                                          from user_table u)
                                                     ) as search
                                                where case
                                                          when '{search_string}' = 'default_value'
                                                              then lower(search.code) like '%'
                                                          else lower(search.name) like lower('%{search_string}%') or
                                                               lower(search.code) like lower('%{search_string}%') end
                                            ) as tmp
                                       order by rn, pointer
                                   ) as tmp2;"""))  # direct sql select into database
            data = rs.fetchall()
            if len(data) == 0:
                await websocket.send_json({"status_code": 404,
                                           "message": "There was an error querying desired data."})
            else:
                items = []
                for row in data:
                    items.append({"name": row[0], "code": row[1], "id": row[2]})
                await websocket.send_json({"status_code": 200,
                                           "message": json.dumps(items, indent=2)})
    except WebSocketDisconnect:
        print("disconnect from websocket")
