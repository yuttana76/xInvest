# Backend

App. invest
-add new model bondAccount. fields below.
compCode
custCode (many to one)
Amount
FromDate
ToDate
Status

    Private Fund
    -add new model privateFundAccound. all filds same as InvestorAccount
    -add new model privateFundBalance. all filds same as AccountBalance

## API URL

    - api url  /me/
    แก้ไขเพิ่มข้อมูล bondAccount,privateFundAccound,privateFundBalance
    ให้ โครงสร้างดังนี้

    Output JSON structure
    {profile
        mfAccounts = InvestorAccount
            balances = AccountBalance
        privateFundAccounds = privateFundAccound
            privateFundBalance = privateFundBalance
        bondAccounts = bondAccount
    }

# Backend

เพิ่ม admin page สำหรับ bondAccount,privateFundAccound,privateFundBalance

# Frontend

Total balance, Net profit, Profit percent เป็นผลรวมของแต่ละกลุ่ม
แต่ต้องแก้ไขเพิ่มข้อมูล bondAccount,privateFundAccound,privateFundBalance
ให้แสดงในหน้า dashboard ออกแบบให้ดูสวยงามไม่สับสน แบ่งตามกลุ่ม MF, Private Fund, Bond
