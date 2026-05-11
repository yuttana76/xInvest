# backend django

- In app "STT-FundConnext"

## 1. fundProfile model

- create model fundProfile spect as below
  and download from fundConext api url /api/files/:businessDate/FundProfile.zip
- execute by celery same as
  'task': 'invest.tasks.run_daily_fundconnext_etl_performance_mf_balance',
  and replace db.(new fundProfile model)
- add this model in admin page.
- admin page add button to download current business date

NO. Name Mandatory Max Length Format
1 Fund Code Y 30 Text
2 AMC_CODE Y 15 Text
3 Fund Name TH Y 500 Text
4 Fund Name EN Y 500 Text
5 Fund Policy Y 1 Text
6 Tax Type N 10 Text
7 FIF Flag Y 1 Text
8 Dividend_Flag Y 1 Text
9 Registration_date C 10 Date
10 Fund Risk Level Y 2 Text
11 FX Risk Flag Y 1 Text
12 FATCA allow Flag Y 1 Text
13 buy_cut_off_time Y 4 Text
14 fst_lowbuy_val N 18 Number (18,2)
15 nxt_lowbuy_val N 18 Number (18,2)
16 sell_cut_off_time Y 4 Text
17 lowsell_val N 18 Number (18,2)
18 lowsell_unit N 18 Number (18,4)
19 lowbal_val N 18 Number (18,2)
20 lowbal_unit N 18 Number (18,4)
21 sell_settlement_day Y 8 Number(8,0)
22 switching_settlement_day Y 8 Number(8,0)
23 switch_out flag Y 1 Text
24 switch_in flag Y 1 Text
25 Fund Class N 30 Text
26 buy period flag Y 1 Text
27 sell period flag Y 1 Text
28 switch in periold flag N 1 Text
29 switch out periold flag N 1 Text
30 buy pre order day N 8 Number(8,0)
31 sell pre order day N 8 Number(8,0)
32 switch pre order day N 8 Number(8,0)
33 Auto redeem fund N 300 Text
34 Beg IPO Date N 10 Text
35 End IPO Date N 10 Text
36 Plain / Complex Fund Y 1 Text
37 Derivatives Flag Y 1 Text
38 lag_allocation_day N 8 Number(8,0)
39 settlement holiday flag Y 1 Text
40 Health Insurrance Y 1 Text
41 Previous Fund Code C 30 Text
42 Investor Alert N 20 Text
43 ISIN N 15 Text
44 lowbal_condition N 1 Text
45 Project Retail Type Y 1 Text
46 Fund Compare Perfermance Description N 100 Text
47 Allocate Digit N 2 Number(2,0)
48 ETF Flag Y 1 Text
49 Trustee N 1000 Text
50 Registrar N 1000 Text
51 Register ID N 15 Text
52 LMTs: Notice Period Amount O 200 Text
53 LMTs: Notice Period % AUM O 200 Text
54 LMTs: ADLs Amount O 200 Text
55 "LMTs: ADLs % AUM
" O 200 Text
56 "LMTs: Liquidity Fee Amount

" O 200 Text
57 "LMTs: Liquidity Fee % AUM

" O 200 Text
58 Other Information URL N 200 Text
59 Currency M 3 Text
60 Complex Fund Presentation O 200 Text
61 Risk Acknowledgement of Complex Fund O 200 Text
62 Redemption Type Condition O 4 Text
63 Internal Use O 1 Text

## 2 FundPerformance model

- create model FundPerformance spect as below
- implement download from fundConext api url /api/files/:businessDate/FundPerformance.zip
- execute by celery same as
  'task': 'invest.tasks.run_daily_fundconnext_etl_performance_mf_balance',
  and replace db.(new FundPerformance model)
- add this model in admin page.
- admin page add button to download current business date

Detail FundPerformance spect
NO. Name Status Type Max Length Possible Value Remark คำอธิบายเพิ่มเติม /Validation / ตัวอย่าง
1 Fund Code M Text 30 "ชื่อย่อกองทุน
BTP"
2 P_YTD_Return O Number (18,5) "ผลตอบแทนตั้งแต่ต้นปี (%)
10.12345"
3 P_3M_Return O Number (18,5) "อัตราผลตอบแทน 3 เดือน (%)
10.12345"
4 P_6M_Return O Number (18,5) "อัตราผลตอบแทน 6 เดือน (%)
10.12345"
5 P_1Y_Return O Number (18,5) "อัตราผลตอบแทน 1 ปี (%) ต่อปี
10.12345"
6 P_3Y_Return O Number (18,5) "อัตราผลตอบแทน 3 ปี (%) ต่อปี
10.12345"
7 P_5Y_Return O Number (18,5) "อัตราผลตอบแทน 5 ปี (%) ต่อปี
10.12345"
8 P_10Y_Return O Number (18,5) "อัตราผลตอบแทน 10 ปี (%) ต่อปี
10.12345"
9 P_SI_Return O Number (18,5) "อัตราผลตอบแทนตั้งแต่จัดตั้งกองทุน (%) ต่อปี
10.12345"
10 P_1Y_SD O Number (18,5) "Standard Deviation 1 ปี (%)
10.12345"
11 P_3Y_SD O Number (18,5) "Standard Deviation 3 ปี (%)
10.12345"
12 P_5Y_SD O Number (18,5) "Standard Deviation 5 ปี (%)
10.12345"
13 P_10Y_SD O Number (18,5) "Standard Deviation 10 ปี (%)
10.12345"
14 NAV Date M Char 8 วันที่ของ NAV ที่ใช้คำนวณ performance ค.ศ. (yyyymmdd)
15 P_1M_Return O Number (18,5) "อัตราผลตอบแทน 1 เดือน (%)
10.12345"
16 P_1W_Return O Number (18,5) "อัตราผลตอบแทน 1 สัปดาห์ (%)
10.12345"
17 Max_DD_1Y O Number (18,5) Maximum Drawdown (%) 1 ปี
18 Max_DD_3Y O Number (18,5) Maximum Drawdown (%) 3 ปี
19 Max_DD_5Y O Number (18,5) Maximum Drawdown (%) 5 ปี
20 Max_DD_10Y O Number (18,5) Maximum Drawdown (%) 10 ปี

## 3 AssetAllocation model

- create model AssetAllocation spect as below
- implement download from fundConext api url /api/files/:businessDate/AssetAllocation.zip
- implement task by celery same as
  'task': 'invest.tasks.run_daily_fundconnext_etl_performance_mf_balance',
  to replace db.(new AssetAllocation model)
- add this model in admin page.
- admin page add button to download current business date

Detail AssetAllocation spect
NO. Name Status Type Max Length Possible Value Remark คำอธิบายเพิ่มเติม /Validation / ตัวอย่าง
1 Fund Code M Text 30 "ชื่อย่อกองทุน
BTP"
2 Investment Type Code M Text 4 "หุ้น (รหัส 101-102)
หุ้นกู้ (รหัส 103 -107)
หน่วยลงทุน (รหัส 108-109,117-121,139)
ใบสำคัญแสดงสิทธิ (รหัส 110 -116,124-129)
เงินฝากธนาคาร P/N และ B/E (รหัส 201-205,216-224)
พันธบัตรรัฐบาลและรัฐวิสาหกิจ (รหัส 206 - 210, 213)
ทองคำแท่ง (รหัส 450)
ตราสารอนุพันธ์(รหัส 401-407)
700 - สินทรัพย์อื่นๆ/หนี้สินอื่นๆ (รหัส 122,211,301-399,500-599) หัก (รหัส 601-699)
903 - รวม = sum (101-599) หัก sum (601-699) "
3 As end of M Text 6 as end of Year Month (YYYYMM) such as 202209
4 Investment Size M Number (20,5) Value in THB

## 4 TopHolding

- create model TopHolding spect as below
- implement download from fundConext api url /api/files/:businessDate/TopHolding.zip
- implement task by celery same as
  'task': 'invest.tasks.run_daily_fundconnext_etl_performance_mf_balance',
  to replace db.(new TopHolding model)
- add this model in admin page.
- admin page add button to download current business date

Detail TopHolding spect

NO. Name Status Type Max Length
1 Fund Code M Text 30
2 Securities Seq M Number (3) 2
3 Securities Name M Text 200
4 Securities Abbreviation Name O Text 50
5 As end of M Text 6
6 Securities Invest Size M Number (5,2)

## 5 CustomerIndividual

- create model CustomerIndividual spect as file in folder /docs/tmp/20260410_MPS_INDIVIDUAL.json Please design data struct(model) for best practice,flexcible, easy to manage

- implement download from fundConext api url /api/files/:businessDate/CustomerProfile.zip
- implement task by celery same as
  'task': 'invest.tasks.run_daily_fundconnext_etl_performance_mf_balance',
- JSON file save data to CustomerIndividual model.Condition is if cardNumber is exist to update but not in db have to insert.
- add this model in admin page.
- admin page add button to download current business date
