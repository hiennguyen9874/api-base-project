# Money Lover request examples

These private web endpoints have no verified public contract. Never commit authorization values,
cookies, or new raw financial responses. The placeholders below are intentionally nonfunctional.

For owner-authorized coverage probes, revoke any exposed session first and run:

```bash
./scripts/capture_moneylover.sh
```

The wizard keeps raw responses in Git-ignored `docs/moneylover/private/` and writes a sanitized
comparison to `docs/moneylover/transaction-capture-summary.json`.

- Danh sách ví, data example in docs/moneylover/list-wallet.json
  ```python
  curl 'https://web.moneylover.me/api/wallet/list' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: <MONEYLOVER_AUTHORIZATION>' \
    -H 'content-type: application/json' \
    -b '<MONEYLOVER_COOKIE>' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/<MONEYLOVER_WALLET_ID_1>' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
    --data-raw '{}'
  ```
- Category list, data example in docs/moneylover/list-category.json
  ```python
  curl 'https://web.moneylover.me/api/category/list-all' \
    -X 'POST' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: <MONEYLOVER_AUTHORIZATION>' \
    -H 'content-length: 0' \
    -b '<MONEYLOVER_COOKIE>' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/<MONEYLOVER_WALLET_ID_1>' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
  ```
- Transaction list, data example in docs/moneylover/list-transaction.json
  ```python
  curl 'https://web.moneylover.me/api/transaction/list' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: <MONEYLOVER_AUTHORIZATION>' \
    -H 'content-type: application/json' \
    -b '<MONEYLOVER_COOKIE>' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/<MONEYLOVER_WALLET_ID_1>' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
    --data-raw '{"walletId":"<MONEYLOVER_WALLET_ID_1>","startDate":"2026-09-01T00:00:00+07:00","endDate":"2026-09-04T23:59:59+07:00"}'
  ```
- debts list, data example in docs/moneylover/list-debts.json
  ```python
  curl 'https://web.moneylover.me/api/transaction/debts' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: <MONEYLOVER_AUTHORIZATION>' \
    -H 'content-type: application/json' \
    -b '<MONEYLOVER_COOKIE>' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/<MONEYLOVER_WALLET_ID_1>' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
    --data-raw '{"accounts":["<MONEYLOVER_WALLET_ID_1>","<MONEYLOVER_WALLET_ID_2>","<MONEYLOVER_WALLET_ID_3>","<MONEYLOVER_WALLET_ID_4>","<MONEYLOVER_WALLET_ID_5>","<MONEYLOVER_WALLET_ID_6>","<MONEYLOVER_WALLET_ID_7>","<MONEYLOVER_WALLET_ID_8>"]}'
  ```
