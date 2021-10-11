from sqlalchemy import text
from sqlalchemy.engine import result
from sqlalchemy.ext.asyncio.session import AsyncSession

async def read_active_sessions(session: AsyncSession):
    sql_text = text(f"""
        select s.id, u.name, u.name_middle
        	from main.session s
        	join main.user u
        		on u.id = s.user_id
        where s.is_active = true
        order by s.id
    """)
    result = await session.execute(sql_text)
    await session.commit()
    return result.all()

async def read_history(session: AsyncSession):
    sql_text  = text("""
        select ac.description, sh.session_time, u.name, u.name_middle, s.id ids, u.id
	        from main.session s
	        join main.sessionhistory sh
	        	on s.id = sh.session_id
	        join main.actioncode ac
	        	on ac.action = sh.action
	        join main.user u
	        	on u.id = s.user_id
	        order by sh.session_time
    """)
    result = await session.execute(sql_text)
    await session.commit()
    return result.all()