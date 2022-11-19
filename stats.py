import streamlit as st
import pandas as pd

from datetime import date, timedelta

from router import router, args
from utils import query_db
from login import login_required

@router(path="/stats")
@login_required
def render():
    st.markdown("# 📈 Statistics Page")
    
    month_ago = (date.today() - timedelta(days=30)).__str__()
    borrow_data = query_db(f"SELECT event_date, count(*) FROM booking_records WHERE event_date IS NOT NULL GROUP BY event_date;")
    return_data = query_db(f"SELECT ret_date, count(*) FROM booking_records WHERE ret_date IS NOT NULL GROUP BY ret_date;")

    data = []
    for i in range(29, -1, -1):
        day = (date.today() - timedelta(days=i))
        daily_data = [0, 0, day]
        
        k = borrow_data.loc[borrow_data['event_date'] == day]
        if not k.empty:
            daily_data[0] = k.iloc[0]['count']
        
        k = return_data.loc[return_data['ret_date'] == day]
        if not k.empty:
            daily_data[1] = k.iloc[0]['count']
        
        data.append(daily_data)
    
    st.markdown("### 👥 User Activities")
    st.line_chart(pd.DataFrame(data, columns=['Borrow Count', 'Return Count', 'Day']), x='Day')
