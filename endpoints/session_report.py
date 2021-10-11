from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import session

from common.read_db import read_active_sessions, read_history

class UserSession(BaseModel):
    timestart:datetime
    timeend:Optional[datetime]
    is_active:bool
    actions:List
    session_len:Optional[timedelta]

async def count_session_len(response):
    now_time = datetime.now()
    for user in response:
        for session_id in response[user]:
            now_session = response[user][session_id]
            if now_session.is_active:
                response[user][session_id].session_len = now_time - now_session.timestart
            else:
                response[user][session_id].session_len = now_session.timeend - now_session.timestart
            response[user][session_id].session_len
    return response

async def report_sessions(session: AsyncSession):
    active_sessions = await read_active_sessions(session)
    active_sessions_dict = []
    for act_s in active_sessions:
        active_sessions_dict.append(act_s['id'])
    data = await read_history(session)
    response = {}
    for ha in data:
        key = f"{ha['name']} {ha['name_middle']}"
        if response.get(key) is None:
            response.update([(key, {})])
        if response[key].get(ha['ids']) is None:
            session_active = False
            if ha['ids'] in active_sessions_dict:
                session_active = True
            session_data = UserSession(
                timestart = ha['session_time'],
                is_active=session_active,
                actions = [ha['description']]
            )
            if not session_active:
                session_data.timeend = ha['session_time']
            response[key].update([(ha['ids'], session_data)])
        else:
            response[key][ha['ids']].actions.append(ha['description'])
            if not response[key][ha['ids']].is_active:
                response[key][ha['ids']].timeend = ha['session_time']
    response = await count_session_len(response)
    return response