# For backend (django)

# Create application. has model below 1,2,3,4

## 1. Investor model

NO. Name PK NULL Format Max Length
1 compCode PK N Char 13
2 custCode PK N Char 13
3 fullNameEn N Char 100
4 fullNameTh N Char 100
4 mobile Y Char 10
6 email N Char 100

## 2. investor_account model

NO. Name PK NULL Format Max Length
1 compCode PK N Char 13
3 custCode PK/FK N Char 13
4 accountID PK N Char 15
5 IC_license FK Y Char 10
6 openDate Y "Date"

## 3. account_balance model

NO. Name PK NULL Mandatory Format Max Length
1 compCode PK N Y Char 15
4 accountID PK/FK N M Char 15
4 fundCode PK N Y Char 30
5 unitBalance N Y Number (18,4) 18
6 amount N Y Number (18,2) 18
7 averageCost N N Number (13,4) 13
8 NAV N Y Number (13,4) 13
9 NAVdate N Y Date

## 4. IC_license model

NO. Name PK NULL Mandatory Format Max Length
1 compCode PK N Y Char 15
2 IC_license PK N Y Char 10
3 fullName N Char 100

# Create api url below (for admin) and access only with jwt authenticated

- Create api url get investor by custCode
- Create api url get investor_account by custCode
- Create api url get account_balance by custCode

# Create api url below (for investor) and access only with jwt authenticated

- Create api url get investor by custCode
- Create api url get investor_account by custCode
- Create api url get account_balance by custCode
