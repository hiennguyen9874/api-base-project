- Danh sách ví, data example in docs/moneylover/list-wallet.json
  ```python
  curl 'https://web.moneylover.me/api/wallet/list' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: AuthJWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzLXRva2VuIiwidXNlcklkIjoiNWQ4NzlhMjBmMDIyOGM0OGZmYWZhZDFiIiwidG9rZW5EZXZpY2UiOiI1ZGIzYjkzZi1jZmFjLTQwN2EtODYwMi1lNjE2MTk0MWM4YmEiLCJjbGllbnRJZCI6IjVhY2FmMzA0YWE2Y2M1MGM3N2Y3ZDIyOCIsImNsaWVudCI6ImtIaVpiRlFPdzVMViIsInNjb3BlcyI6bnVsbCwiaWF0IjoxNzg4NTE5NzU3LCJleHAiOjE3ODkxMjQ1NTd9.usT5N4rs9Q4ixzAkzfOikSjaWgCVvncshAN21wYnOYg' \
    -H 'content-type: application/json' \
    -b '_ga=GA1.1.1924344647.1763917048; _ga_SGTSQ06VHD=GS2.1.s1783349456$o12$g1$t1783349993$j60$l0$h0; cf_clearance=RUyo26vMmAp3F6xz3zU_UEVv__SdIarc35XdXwDZ2ws-1788537070-1.2.1.1-onk0mkqTb6FhfjQaC.BBILuoxdyhzaSmetNCZI5apkGMsDJVrt3GZdZNxNAiU_Z7gQEG84Z_D9ZDWxou8uq3codvaCjzfFixk36aogqB_t3alWo_Dn4TeQE72sq_17VJUDUEY.LvrSOGWpsBJeK6Xn3WU7NQKMAi5k_azpyL9ZA._otIXeWA6Zqh2ppitNLzy0isN_X2WInk5UaQevZ5zOX9JB0w.SaQDROSpAmQpb2WvKunCi0Jnn7lh5zHsaqTlGIrHwWl.riD3CKMFL.cEniksm41Y_SDXdHDr30skcQGzf8j1gTeWc28XNwRcaPAYtqKe6nMQ9bk0R8tezGIkZ4xfgFBPncxNjIwLhbgswU' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/7d761800aa2e41bda0a4cbb2a6ae1966' \
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
    -H 'authorization: AuthJWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzLXRva2VuIiwidXNlcklkIjoiNWQ4NzlhMjBmMDIyOGM0OGZmYWZhZDFiIiwidG9rZW5EZXZpY2UiOiI1ZGIzYjkzZi1jZmFjLTQwN2EtODYwMi1lNjE2MTk0MWM4YmEiLCJjbGllbnRJZCI6IjVhY2FmMzA0YWE2Y2M1MGM3N2Y3ZDIyOCIsImNsaWVudCI6ImtIaVpiRlFPdzVMViIsInNjb3BlcyI6bnVsbCwiaWF0IjoxNzg4NTE5NzU3LCJleHAiOjE3ODkxMjQ1NTd9.usT5N4rs9Q4ixzAkzfOikSjaWgCVvncshAN21wYnOYg' \
    -H 'content-length: 0' \
    -b '_ga=GA1.1.1924344647.1763917048; _ga_SGTSQ06VHD=GS2.1.s1783349456$o12$g1$t1783349993$j60$l0$h0; cf_clearance=RUyo26vMmAp3F6xz3zU_UEVv__SdIarc35XdXwDZ2ws-1788537070-1.2.1.1-onk0mkqTb6FhfjQaC.BBILuoxdyhzaSmetNCZI5apkGMsDJVrt3GZdZNxNAiU_Z7gQEG84Z_D9ZDWxou8uq3codvaCjzfFixk36aogqB_t3alWo_Dn4TeQE72sq_17VJUDUEY.LvrSOGWpsBJeK6Xn3WU7NQKMAi5k_azpyL9ZA._otIXeWA6Zqh2ppitNLzy0isN_X2WInk5UaQevZ5zOX9JB0w.SaQDROSpAmQpb2WvKunCi0Jnn7lh5zHsaqTlGIrHwWl.riD3CKMFL.cEniksm41Y_SDXdHDr30skcQGzf8j1gTeWc28XNwRcaPAYtqKe6nMQ9bk0R8tezGIkZ4xfgFBPncxNjIwLhbgswU' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/7d761800aa2e41bda0a4cbb2a6ae1966' \
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
    -H 'authorization: AuthJWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzLXRva2VuIiwidXNlcklkIjoiNWQ4NzlhMjBmMDIyOGM0OGZmYWZhZDFiIiwidG9rZW5EZXZpY2UiOiI1ZGIzYjkzZi1jZmFjLTQwN2EtODYwMi1lNjE2MTk0MWM4YmEiLCJjbGllbnRJZCI6IjVhY2FmMzA0YWE2Y2M1MGM3N2Y3ZDIyOCIsImNsaWVudCI6ImtIaVpiRlFPdzVMViIsInNjb3BlcyI6bnVsbCwiaWF0IjoxNzg4NTE5NzU3LCJleHAiOjE3ODkxMjQ1NTd9.usT5N4rs9Q4ixzAkzfOikSjaWgCVvncshAN21wYnOYg' \
    -H 'content-type: application/json' \
    -b '_ga=GA1.1.1924344647.1763917048; _ga_SGTSQ06VHD=GS2.1.s1783349456$o12$g1$t1783349993$j60$l0$h0; cf_clearance=RUyo26vMmAp3F6xz3zU_UEVv__SdIarc35XdXwDZ2ws-1788537070-1.2.1.1-onk0mkqTb6FhfjQaC.BBILuoxdyhzaSmetNCZI5apkGMsDJVrt3GZdZNxNAiU_Z7gQEG84Z_D9ZDWxou8uq3codvaCjzfFixk36aogqB_t3alWo_Dn4TeQE72sq_17VJUDUEY.LvrSOGWpsBJeK6Xn3WU7NQKMAi5k_azpyL9ZA._otIXeWA6Zqh2ppitNLzy0isN_X2WInk5UaQevZ5zOX9JB0w.SaQDROSpAmQpb2WvKunCi0Jnn7lh5zHsaqTlGIrHwWl.riD3CKMFL.cEniksm41Y_SDXdHDr30skcQGzf8j1gTeWc28XNwRcaPAYtqKe6nMQ9bk0R8tezGIkZ4xfgFBPncxNjIwLhbgswU' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/7d761800aa2e41bda0a4cbb2a6ae1966' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
    --data-raw '{"walletId":"7d761800aa2e41bda0a4cbb2a6ae1966","startDate":"2026-09-01T00:00:00+07:00","endDate":"2026-09-04T23:59:59+07:00"}'
  ```
- debts list, data example in docs/moneylover/list-debts.json
  ```python
  curl 'https://web.moneylover.me/api/transaction/debts' \
    -H 'accept: application/json' \
    -H 'accept-language: vi,en;q=0.9,zh-CN;q=0.8,zh;q=0.7' \
    -H 'authorization: AuthJWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWNjZXNzLXRva2VuIiwidXNlcklkIjoiNWQ4NzlhMjBmMDIyOGM0OGZmYWZhZDFiIiwidG9rZW5EZXZpY2UiOiI1ZGIzYjkzZi1jZmFjLTQwN2EtODYwMi1lNjE2MTk0MWM4YmEiLCJjbGllbnRJZCI6IjVhY2FmMzA0YWE2Y2M1MGM3N2Y3ZDIyOCIsImNsaWVudCI6ImtIaVpiRlFPdzVMViIsInNjb3BlcyI6bnVsbCwiaWF0IjoxNzg4NTE5NzU3LCJleHAiOjE3ODkxMjQ1NTd9.usT5N4rs9Q4ixzAkzfOikSjaWgCVvncshAN21wYnOYg' \
    -H 'content-type: application/json' \
    -b '_ga=GA1.1.1924344647.1763917048; _ga_SGTSQ06VHD=GS2.1.s1783349456$o12$g1$t1783349993$j60$l0$h0; cf_clearance=RUyo26vMmAp3F6xz3zU_UEVv__SdIarc35XdXwDZ2ws-1788537070-1.2.1.1-onk0mkqTb6FhfjQaC.BBILuoxdyhzaSmetNCZI5apkGMsDJVrt3GZdZNxNAiU_Z7gQEG84Z_D9ZDWxou8uq3codvaCjzfFixk36aogqB_t3alWo_Dn4TeQE72sq_17VJUDUEY.LvrSOGWpsBJeK6Xn3WU7NQKMAi5k_azpyL9ZA._otIXeWA6Zqh2ppitNLzy0isN_X2WInk5UaQevZ5zOX9JB0w.SaQDROSpAmQpb2WvKunCi0Jnn7lh5zHsaqTlGIrHwWl.riD3CKMFL.cEniksm41Y_SDXdHDr30skcQGzf8j1gTeWc28XNwRcaPAYtqKe6nMQ9bk0R8tezGIkZ4xfgFBPncxNjIwLhbgswU' \
    -H 'dataformat: json' \
    -H 'origin: https://web.moneylover.me' \
    -H 'priority: u=1, i' \
    -H 'referer: https://web.moneylover.me/wallet/7d761800aa2e41bda0a4cbb2a6ae1966' \
    -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
    -H 'sec-ch-ua-mobile: ?0' \
    -H 'sec-ch-ua-platform: "Linux"' \
    -H 'sec-fetch-dest: empty' \
    -H 'sec-fetch-mode: cors' \
    -H 'sec-fetch-site: same-origin' \
    -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
    --data-raw '{"accounts":["7d761800aa2e41bda0a4cbb2a6ae1966","f46abfb49cf74faf88440ba9e62c61dd","1b7a2b297fd94921b278ae97915703bd","7aa5afa8158d45aeafbf15b2f8050d49","8b34f77fd0274a2c92c00d42d695450a","444e2066281e4648b2575534e88f3e7a","5bdfb0e4003549b7b7dacd0a3a920500","d92dc93eb74546d3872339e49c98c6a6"]}'
  ```
