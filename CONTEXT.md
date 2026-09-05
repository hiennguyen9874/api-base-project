# CashLens Finance

CashLens is a read-only financial mirror that distinguishes provider-observed wallet state from reports derived from imported transactions.

## Language

**Income & spending**:
Ordinary income and expense eligible for reporting; it excludes transfers, debt movements, excluded transactions, and transactions whose classification is unknown.
_Avoid_: Cash flow, all money in and out

**Wallet movement**:
Money entering or leaving a wallet through any transaction with a verified direction, including transfers and debt movements regardless of reporting exclusion.
_Avoid_: Income & spending, balance change

**Current balance**:
The latest provider-observed balance for a wallet and currency, carrying the time it was observed; absence of an observation is unknown, not zero.
_Avoid_: Calculated balance, live balance

**Accounting day**:
The calendar day used to assign a transaction to reports, interpreted in the reporting timezone and distinct from creation, synchronization, or observation time.
_Avoid_: Transaction timestamp, sync date

**Reporting period**:
An inclusive range of accounting days selected for a report. An incomplete current period may be compared both with matched elapsed days and with the complete preceding period.
_Avoid_: Timestamp window

**Currency total**:
A financial aggregate containing values from exactly one known currency; CashLens has no mixed-currency grand total without an explicit conversion model.
_Avoid_: Overall total, converted total

**Reporting wallet scope**:
The wallets whose transactions contribute to a report. It includes archived-wallet history by default and is independent of a wallet's current-balance exclusion.
_Avoid_: Current-balance scope

**Wallet category**:
A category identified within one wallet and optionally related to a parent category in that wallet. Matching category names in different wallets do not establish shared identity.
_Avoid_: Global category

**Transaction explorer**:
The searchable history of all imported transaction types, including ordinary, transfer, debt, excluded, and unclassified movements.
_Avoid_: Spending list

**Transaction magnitude**:
The non-negative amount recorded for a transaction before applying its verified direction. Unexpected negative source amounts are unresolved data, not inverse movements.
_Avoid_: Signed amount

**Unclassified transaction**:
A transaction whose financial meaning or direction is not supported by a reviewed source-semantic rule. It remains visible but does not silently contribute to financial aggregates.
_Avoid_: Other income, other expense

**Report coverage**:
The attempted wallet and accounting-day scopes represented by a report, together with missing scopes and records excluded because their financial meaning is unresolved.
_Avoid_: Complete history

**Unresolved category**:
A wallet-level reporting bucket for a transaction whose own classification is usable but whose category ancestry is missing or cyclic.
_Avoid_: Uncategorized

**Canonical transaction**:
CashLens's accepted representation of one provider transaction, assembled under explicit source-precedence and classification rules while retaining contradictory source evidence separately.
_Avoid_: Latest response, ledger entry

**Source variant**:
One endpoint's observed representation of a provider entity; multiple source variants may refer to the same canonical transaction without being interchangeable.
_Avoid_: Duplicate transaction

**Quarantined source record**:
Retained source evidence that CashLens could not safely apply because it was malformed or materially contradicted another source variant.
_Avoid_: Failed transaction, deleted record

**Money Lover connection**:
The association between one CashLens owner and one verified remote Money Lover identity. It owns imported evidence and synchronization history but does not retain a reusable Money Lover access token.
_Avoid_: Saved login, wallet account

**Synchronization run**:
One explicit owner-requested attempt to import a selected synchronization mode, with durable progress and an outcome independent of previously accepted financial data.
_Avoid_: Login session, report refresh
