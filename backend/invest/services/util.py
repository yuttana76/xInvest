def calculate_performance(unit_balance, nav, average_cost):
    """
    คำนวณกำไร/ขาดทุน และ % ROI
    """
    unit_balance = float(unit_balance)
    nav = float(nav)
    avg_cost = float(average_cost)

    # 1. มูลค่าตลาดปัจจุบัน (Market Value)
    market_value = unit_balance * nav
    
    # 2. ต้นทุนทั้งหมด (Total Cost)
    total_cost = unit_balance * avg_cost
    
    # 3. กำไร/ขาดทุนที่ยังไม่รับรู้ (Unrealized Gain/Loss)
    unrealized_gain = market_value - total_cost
    
    # 4. ROI % (ป้องกันการหารด้วยศูนย์)
    roi_percent = (unrealized_gain / total_cost * 100) if total_cost > 0 else 0
    
    return market_value, unrealized_gain, roi_percent

