# Design System: CashLens

## 1. Visual Theme & Atmosphere

**Design read:** Reading this as a private, Vietnamese, analysis-first finance application for its signed-in owner, with a precise, calm visual language built on the existing Base UI and source-owned shadcn foundation.

**Direction: Bàn điều khiển phân tích.** CashLens should feel like a carefully typeset financial workspace, not a banking advertisement. Small observed balances establish context; spending, comparisons and explainable transaction evidence receive the visual emphasis. Quiet zinc surfaces, deep teal interaction accents, aligned figures and well-spaced rows create confidence without implying that imported history is complete.

| Design dial | Value | Consequence |
| --- | --- | --- |
| `DESIGN_VARIANCE` | 3/10 | Predictable application structure; asymmetry only to prioritize analysis over supporting breakdowns |
| `MOTION_INTENSITY` | 2/10 | Brief interaction feedback and panel transitions; no ambient animation |
| `VISUAL_DENSITY` | 6/10 | Daily-app density, readable analytical panels and compact desktop history |

### Design method and applicability

Apply **design-taste-frontend first** for brief inference, existing-foundation audit, typography, restraint and contextual anti-patterns. Apply **stitch-design-taste second** to encode the result as precise semantic screen-generation instructions in this file.

The first skill explicitly excludes dashboards, data tables and multi-step product flows. Its landing-page hero, image, bento, section-variation and list-length prescriptions do not govern this application. Use the installed Base UI primitives, TanStack Table and Recharts for those product surfaces. Similarly, Stitch's inline-image headlines, perpetual loops and waterfall list entrances are deliberately not used: financial clarity, accessibility and stable reading order take precedence. No marketing hero, stock photography or generated artwork is needed.

### Authority and scope

1. [Issue #9: Money Lover mirror MVP and phased implementation gates](https://github.com/hiennguyen9874/CashLens/issues/9) defines the accepted product, Vietnamese variant A and superseding decisions.
2. [docs/database-design.md](docs/database-design.md) supplies financial semantics and evidence limitations where not superseded.
3. [web/AGENTS.md](web/AGENTS.md) defines frontend architecture, security and generated-client conventions.
4. This file defines presentation and interaction. It does not create API contracts, implemented features or launch readiness.

Issue #9 supersedes the older proposal's reusable credentials, scheduled sync, paused connection state and debt-balance dashboards. The design has **manual, fresh-token sync only**, connection states `unbound`, `ready`, `auth_required`, Full backfill beginning January 2020, and searchable debt movements without a debt dashboard.

Financial APIs are proposed, not currently implemented. Financial screen generation is design work only. Production implementation follows the issue's strict offline import → live-sync resilience/evidence → financial API/OpenAPI → Vietnamese UI gates. Do not create invented endpoints or browser mocks to bypass them.

### Existing foundation audit

The current `web/src/routes/index.tsx` is a centered foundation placeholder, not an established dashboard. `web/src/index.css` uses Arial and generic monochrome shadcn tokens with a 10px base radius. Preserve CashLens naming, React/Vite, existing authentication, Router/Query, Tailwind v4, Base UI and Lucide. Replace the placeholder composition, English starter copy and generic typography. There is no existing financial navigation or custom brand mark to preserve. Existing user/item behavior is outside this visual specification and must not be removed.

---

## 2. Color Palette & Roles

Use one zinc-neutral family and one **Deep Teal** interaction accent. Semantic warning/error colors are reserved for actual conditions, not decorative accents or arbitrary financial series. No gradients, neon, glass, pure black or alternating light/dark sections.

Default to the system theme. Offer `Theo hệ thống`, `Sáng`, `Tối` in the shell account menu. Apply one theme to the whole application, including portals, sheets, menus and charts. Light is the canonical composition reference; dark has equal hierarchy and full functionality.

| Semantic token | Light: name and hex | Dark: name and hex | Functional role |
| --- | --- | --- | --- |
| `canvas` | Zinc Mist `#F4F4F5` | Zinc Night `#18181B` | Application background |
| `surface` | Soft White `#FAFAFA` | Raised Charcoal `#202023` | Sidebar, analytical panels, table, inputs |
| `surface-overlay` | Soft White `#FAFAFA` | Overlay Charcoal `#27272A` | Modal, popover, detail sheet |
| `surface-subtle` | Zinc Wash `#EDEDEF` | Zinc Recess `#27272A` | Quiet grouped rows, skeleton base, hover |
| `text-primary` | Graphite `#18181B` | Pale Zinc `#FAFAFA` | Headings, money, body |
| `text-secondary` | Zinc Ink `#52525B` | Silver Text `#D4D4D8` | Supporting copy, timestamps, labels |
| `text-muted` | Zinc Mid `#62626C` | Muted Silver `#A1A1AA` | Placeholders and less prominent readable text |
| `border-subtle` | Zinc Rule `#D4D4D8` | Charcoal Rule `#3F3F46` | Nonessential row/panel separators |
| `border-control` | Zinc Edge `#71717A` | Silver Edge `#92929C` | Essential input and outlined control boundaries |
| `accent` | Deep Teal `#176B60` | Clear Teal `#73C7B7` | Primary action, selected navigation, focus, income series |
| `accent-hover` | Pressed Teal `#12564D` | Light Teal `#8CD4C6` | Primary hover/active fill |
| `accent-soft` | Teal Wash `#E2EFEC` | Teal Recess `#203B36` | Selected rows/nav, informational emphasis |
| `on-accent` | Soft White `#FAFAFA` | Zinc Night `#18181B` | Primary-button text |
| `warning` | Ochre Ink `#805700` | Pale Amber `#E7BF73` | Partial coverage, unresolved evidence, review required |
| `warning-soft` | Pale Amber Wash `#F5EDDA` | Amber Recess `#382F20` | Compact warning surface |
| `danger` | Brick Ink `#A1333A` | Soft Coral `#F0A0A5` | Failed requests, rejected credentials, invalid input |
| `danger-soft` | Rose Wash `#F7E7E9` | Brick Recess `#3D2529` | Error surface |

### Application rules

- Primary body text targets 7:1 contrast; all normal text, including placeholders and chart labels, must meet 4.5:1. Essential non-text controls and focus indicators must meet 3:1 against adjacent surfaces.
- Subtle borders organize content; they are not the sole indication of a clickable control. Use `border-control` for essential outlines.
- Use teal for selected/interactive elements and successful semantic confirmation. Use label plus icon, never a color-only status dot.
- Spending is graphite in light mode and silver in dark mode, not red. Borrowing is not a green gain. A higher or lower expense comparison is described factually, not judged automatically.
- Unselected category bars are neutral. Selection uses teal. Do not introduce a rainbow palette to distinguish categories.
- Map these tokens into existing CSS custom properties and shadcn aliases: `background=canvas`, `card=surface`, `popover=surface-overlay`, `primary=accent`, `primary-foreground=on-accent`, `muted=surface-subtle`, `muted-foreground=text-muted`, `ring=accent`, `destructive=danger`. The shadcn `accent` alias means `accent-soft`, not a second brand hue.
- Theme tokens are centrally defined in `web/src/index.css` when implemented. Do not scatter raw hex values through features or mix CSS-variable theming with ad hoc theme overrides.

---

## 3. Typography Rules

**Primary font:** Geist, weights 400, 500 and 600. Use for Vietnamese navigation, body, headings and ordinary financial figures.

**Evidence font:** Geist Mono, weights 400 and 500. Use selectively for complete source IDs and machine-readable identifiers, not for entire paragraphs or all timestamps.

Self-host licensed WOFF2 assets with full Vietnamese glyph coverage, including combined diacritics. Use `font-display: swap`; verify `Đồng bộ`, `Khoản thu`, `Chưa phân loại` and long wallet names at every weight. Fonts are a future asset requirement, not already installed. Fallbacks are `ui-sans-serif, system-ui, sans-serif` and `ui-monospace, monospace`. No external font tracking requests, Inter, display serif or icon-font substitutes.

| Role | Desktop size / line height | Mobile size / line height | Weight / tracking |
| --- | --- | --- | --- |
| CashLens wordmark | 20px / 28px | 20px / 28px | 600 / -0.025em |
| Page title | 28px / 36px | 24px / 32px | 600 / -0.025em |
| Main analytical number | 32px / 40px | 28px / 36px | 600 / -0.025em |
| Compact balance | 20px / 28px | 20px / 28px | 600 / -0.015em |
| Panel title | 18px / 26px | 18px / 26px | 600 / -0.015em |
| Body and form input | 16px / 24px | 16px / 24px | 400 / normal |
| Controls, table body, metadata | 14px / 20px | 14px / 20px | 400 or 500 / normal |
| Chart label, compact badge | 12px / 18px | 12px / 18px | 500 / normal |

Use fluid page titles between 24px and 28px and analytical numbers between 28px and 32px. Never shrink an amount until illegible to fit a container. Let its currency/context move to a separate line or expand the row. Body paragraphs have a maximum measure of 65ch. Do not crop Vietnamese accents with tight line heights.

### Financial typography and locale

- Set `font-variant-numeric: tabular-nums lining-nums` on amounts, comparison values and counts. Right-align amount columns; left-align labels. Avoid animated counting or proportional digit jitter.
- Interface copy is Vietnamese, except proper names, currency codes and source evidence. Preserve original wallet/category/counterparty text, including meaningful Unicode and line breaks in detail.
- Use `vi-VN` grouping and decimal separators with an explicit ISO currency code: an illustrative exact decimal string `"1234567.50"` in USD displays as `1.234.567,50 USD`. This is formatting guidance, not a real balance or fixture.
- Never use `Number`, `parseFloat` or implicit arithmetic to format money or bigint IDs. Use an exact decimal-string-safe formatter informed by `Intl` locale rules. Default currency fraction digits must not silently discard nonzero source precision; expose the full exact value in detail and accessible text.
- Compact axis labels may abbreviate with `nghìn` or `triệu`, marked as chart-scale approximations. Headline totals, table amounts and tooltip evidence remain exact.
- Distinguish source magnitude from movement: show a direction label and visual plus/minus only when supplied classification verifies direction. Unknown direction displays the exact source value without an inferred sign.
- `0 VND` means a known zero. `Không rõ` means no usable observation. `Chưa có dữ liệu` means no imported evidence. Loading is a skeleton, not any of these values.
- Accounting dates display as `dd/MM/yyyy`; chart ticks may use `dd/MM`. Do not parse date-only values through timezone-shifting instant conversions. Instants display in `Asia/Ho_Chi_Minh`; full timestamps include `GMT+7` in detail. Relative freshness text must also expose an absolute timestamp.

---

## 4. Component Stylings

### Shape, spacing and elevation

Use a restrained radius hierarchy: 4px for small icon backplates, 8px for buttons/inputs/filter chips, 12px for panels/popovers/dialogs, and 16px for the top corners of mobile sheets. Only compact status badges may use a full-pill radius. Do not use inflated 40px cards.

Spacing scale: **4, 8, 12, 16, 20, 24, 32, 40, 48px**. Use 8px between icon and label; 8px between form label and field; 16px between fields; 24px desktop or 16px mobile panel padding. Major report sections are 24px apart, not marketing-sized 96px gaps.

Most content is flat: 1px subtle outlines or whitespace, no shadows. A raised overlay may use `0 12px 32px rgba(24,24,27,0.12)` in light and `0 12px 32px rgba(12,12,15,0.32)` in dark. No backdrop blur. A modal scrim is charcoal at 40% opacity in light, 64% in dark.

### Buttons and links

- Standard button: 44px minimum height, 16px horizontal padding, 14px/20px medium text, 8px radius.
- Primary: solid teal with `on-accent` text. Use for the next consequential action, normally `Đồng bộ ngay` or `Bắt đầu đồng bộ`.
- Secondary: surface fill, `border-control`, primary text. Use for filters, secondary navigation and cancellation confirmation.
- Quiet: transparent, secondary text; readable hover surface. Links are teal and underlined on hover/focus, with a non-color affordance where inline prose requires it.
- Hover changes fill only. Pressed primary buttons may translate down 1px; focus never depends on animation. Disabled buttons do not react and have an adjacent explanation when their availability is non-obvious.
- Use a 2px teal focus outline with 2px offset. Every icon-only control has a 44×44px target and a Vietnamese accessible name.
- Keep action labels on one line. Use one label per intent throughout the application. Do not populate every analytical panel with a redundant primary action.

### Icons and identity

Keep installed `lucide-react`, one outline family at stroke width 1.75. Use 20px icons for navigation and ordinary controls; 16px inside badges. Icons support visible labels and never encode classification alone. Use the CashLens text wordmark; do not invent a new elaborate logo or copy Money Lover's visual branding. No avatars or remote photographs are necessary.

### Inputs, selectors and chips

- Inputs are at least 44px tall, 16px type, 12px horizontal padding, surface fill and an essential boundary.
- Visible label above every field, helper below when needed, error immediately below in `danger`. Placeholders are examples, never labels.
- Multi-select options support keyboard search, selected checkmarks and long wrapped wallet names. IDs remain hidden identity, not display labels.
- Applied filters are 8px-radius chips with readable text and a separately named remove action. Their target area remains 44px high even if the visual chip is compact. Wrap to new lines on mobile; no horizontal chip carousel.
- Currency selection never implies conversion. Category selection requires exactly one wallet. Amount bounds require exactly one currency. Disable incompatible controls with explanatory text; never silently narrow or reset the user's selections.
- A filter sheet has explicit `Áp dụng` and `Đặt lại` actions, with draft state local until apply. On mobile, stack full-width actions if both labels cannot fit comfortably.

### Status badges and notices

Use short label plus icon: `Đang đồng bộ`, `Chưa đầy đủ`, `Cần kiểm tra`, `Chưa phân loại`, `Cần token mới`. Use warning for uncertainty, danger for a failed operation, neutral for historical/structural labels. Keep badges legible rather than faded.

A compact notice has a 20px status icon, one or two lines of explanation and `Xem chi tiết`. On mobile it wraps naturally. Persistent financial limitations belong adjacent to the affected result, not only in a toast. Keep freshness and completeness separate even when sharing a notice region.

### Panels and tables

An analytical panel contains its own heading, contextual controls, visualization and evidence footer. Do not nest a bordered card around every internal metric. Organize related values with whitespace and, when necessary, one internal divider.

Desktop transaction rows are 56px minimum, 72px when a second line or issue badge is needed. Header height is 44px. Use a single bottom separator between rows, a subtle hover fill and teal-tinted selection. No zebra striping by default. Amounts remain right-aligned and untruncated. Never imply editing with checkboxes, drag handles, kebab mutation menus or floating add buttons.

### Dialogs, sheets and detail

Use Base UI accessibility behavior for focus trapping, Escape, initial focus and focus return. Desktop token dialog is 480px wide with a viewport-safe maximum, 24px padding and 12px radius. Desktop transaction detail is a 480px right overlay panel, maximum 92vw. It does not squeeze the table into a broken layout.

Mobile transaction detail is full-screen, with a visible back/close control and independently scrolling content. Mobile filters and wallet observation context use a bottom sheet, maximum 90dvh, with 16px top corners. Content and footer account for keyboard and safe-area insets. Overlays are the explicit exception to the no-overlapping-content rule; ordinary page elements never overlap.

### Loading, empty and errors

- Skeletons match the final metric line, chart plot, row height and panel structure. Use static neutral blocks, no shimmer loop or fake chart trend.
- First import: `Chưa có dữ liệu để phân tích` with `Đồng bộ Money Lover để bắt đầu. Các phần đã nhập sẽ xuất hiện dần.` and the shared `Đồng bộ ngay` action.
- Valid empty search: `Không có giao dịch phù hợp` with `Thử đổi thời gian hoặc bỏ bớt bộ lọc.` and `Xóa bộ lọc`. Do not suggest another sync unless missing coverage is the actual cause.
- Unknown balance: `Không rõ`, followed by `Chưa có lần ghi nhận số dư.` No numeric placeholder.
- CashLens read failure: `Không tải được dữ liệu CashLens.` with `Thử lại`. Preserve cached content only if clearly marked as previously loaded, not refreshed.
- Provider failure: `Lần đồng bộ chưa hoàn tất. Dữ liệu đã nhập vẫn được giữ lại.` Link to sync detail; do not replace a usable report with a full-page error.
- Auth failure in a provider run is not a CashLens login failure. Existing CashLens session expiry uses existing authentication behavior and never reveals cached owner data to another session.

---

## 5. Layout Principles

### Information architecture

Exactly four primary destinations, in this order:

| Destination | Purpose | Primary content |
| --- | --- | --- |
| `Tổng quan` | Analysis-first landing | Compact balances, income/spending, comparisons, movement, categories and coverage |
| `Giao dịch` | Read-only evidence explorer | Search, structured filters, stable paginated rows, transaction detail |
| `Đồng bộ` | Manual import and health | Connection, current/last run, attempted coverage, errors and recovery |
| `Ví` | Observed balance context | Wallets by currency, observation timestamps and balance inclusion controls |

Categories are wallet-scoped filters and breakdowns, not an extra primary destination. Do not add Budgets, Investments, Net worth, AI advice, Debt balances or a marketing Home. UI route paths remain an implementation decision; these labels do not authorize new API endpoints.

### Desktop shell: reference 1440×900

- Persistent left sidebar: 224px, full viewport height, surface fill and 1px right rule.
- Wordmark at top with 24px inset; four 44px navigation rows below. Selected destination uses teal wash, teal icon/text and medium weight.
- Account/theme menu at the bottom, separated from financial navigation. Never display the provider token or remote membership list here.
- Main workspace has 32px side padding, 24px top padding and a maximum inner width of 1400px. It expands naturally within the remaining viewport.
- Page header has title and concise descriptive context on the left, shared sync action/status on the right. Minimum height 56px; no giant masthead.
- Content uses a 12-column grid with 24px gaps. The first analytical split is 8 columns for income/spending and 4 for categories. Other data collections use rows rather than repeated bento cards.
- Header controls must fit one line where designed for desktop. At narrower widths, move secondary filters into a filter control, not a second navigation line.

### Responsive behavior

| Width | Shell and layout |
| --- | --- |
| 1280px and above | 224px sidebar, 32px main padding, 8:4 analysis split |
| 1024px to 1279px | 200px sidebar, 24px main padding; stack analytical panels if each cannot retain a readable plot/label width |
| 768px to 1023px | 64px top bar with labeled navigation drawer; 24px content padding; one main analytical column |
| Below 768px | 56px top bar, bottom navigation, 16px content padding; every major multi-column content section becomes one column |

At mobile width, retain the four bottom destinations with icon plus 12px label. Bottom bar is 64px plus safe-area inset. Reserve its full height plus 16px below page content. Do not hide navigation labels or reduce touch targets.

Reference mobile is **390×844**. Also protect 320px width, 200% zoom and long localized text. No page-level horizontal overflow. Search remains visible above transaction rows; filter chips wrap below it. Tables become stacked transaction records below 768px, not tiny compressed desktop tables. Currency groups and metric blocks stack vertically. Individual record label/value pairs may share a line when readable; this is not a multi-column page layout.

Use CSS Grid and `minmax(0, 1fr)`, not percentage calculations. Full-height shells use `min-height: 100dvh`; sheets use viewport-safe dynamic heights. Avoid multiple scroll containers except intentional modal/detail content. Sticky headers must not obscure keyboard focus or the last row.

### Layer scale

`0` content; `10` sticky table/filter header; `20` application navigation; `30` non-modal popover; `40` modal scrim; `50` dialog/sheet; `60` dialog-owned popover; `70` toast. Tooltip layers follow their owning overlay context. Do not use arbitrary high z-index values.

---

## 6. Screen Specifications

### 6.1 Tổng quan: analytical landing

The first impression is useful financial context, not branding. On a 1440×900 viewport, the page title, filters, compact balances and the main income/spending chart should be visible without scrolling. Lower movement detail may continue below the fold.

```text
┌ Sidebar ┐  Tổng quan                         Đồng bộ ngay
│         │  Period / wallets / currencies     Active filters
│         │  Compact observed balances, grouped by currency
│         │  Freshness and coverage notice when relevant
│         │  ┌ Thu nhập & chi tiêu ─────────┐ ┌ Chi theo danh mục ┐
│         │  │ Income / spending / net     │ │ Wallet grouping  │
│         │  │ Matched-period comparison  │ │ Ranked bars      │
│         │  │ Paired-column time chart   │ │ Category detail  │
│         │  └────────────────────────────┘ └───────────────────┘
│         │  Biến động ví: signed daily movement and scope context
└─────────┘  Coverage and data-quality explanation
```

**Header and filters**

- Title `Tổng quan`. Optional one-line context: `Phân tích dữ liệu đã nhập từ Money Lover.`
- Date presets: `Tháng này`, `Tháng trước`, `3 tháng gần đây`, `6 tháng gần đây`, `12 tháng gần đây`, `Năm nay`, `Tùy chọn`.
- Actual period boundaries come from the server and remain visible. Custom start/end controls are inclusive for the owner; their API representation is half-open.
- Wallet and currency multi-selects own report scope. Multiple currencies render distinct currency report sections; no combined total or shared financial axis.

**Compact balance strip**

Label `Số dư ghi nhận`, followed by an explicit currency amount or `Không rõ`. Use 20px figures, not oversized hero cards. The strip has one flat surface and currency groups separated by spacing/rules. Show `Theo từng lần ghi nhận của ví`, linking to per-wallet observations; never imply all balances share one effective timestamp. Open the `Ví` destination or an observation sheet carrying current filters.

The selected accounting period does not turn current observations into historical balances. Explain `Số dư ghi nhận không phụ thuộc kỳ phân tích.` Keep balance eligibility controls separate from historical report filters.

**Thu nhập & chi tiêu**

- Use a dominant 32px `Chi tiêu` amount, with quieter `Thu nhập` and `Thu nhập ròng` values in a flat metric rail. This is not three separate equal cards.
- On mobile, show these as three stacked label/value blocks with no nested containers.
- Display compact factual comparisons such as `Tăng so với cùng số ngày kỳ trước`, with exact server-provided delta. Provide the explicit two date ranges in a comparison disclosure.
- For active calendar presets, headline comparison is matched elapsed days, capped to prior period length; show `Toàn kỳ trước` as secondary context. Custom ranges compare to the immediately preceding equal-length range only.
- If the server cannot supply a meaningful percentage, show a factual amount difference or `Không có cơ sở so sánh`, never infinity or a client-computed percentage.
- Chart below the metric rail: paired income/spending columns, 240px plot area desktop, 200px mobile, using server-provided accounting-day/month buckets. Legend and exact accessible table accompany it.
- Click a metric or bar through a named drill-down action to `Giao dịch` with its exact date, wallet, currency, classification, inclusion and bucket predicates. A spending bar must not open all outgoing movements.

**Chi theo danh mục**

Use ranked horizontal bars with category label, wallet context and exact amount. Show up to six server-ranked entries in the overview; `Xem giao dịch` opens matching evidence. If the server provides an aggregated remainder, label it explicitly; never compute one in the browser.

For multiple wallets, show wallet headings then wallet-scoped categories. For one wallet, allow root/subtree navigation with a visible breadcrumb. `Danh mục chưa xác định` remains a visible bucket when otherwise valid spending has missing/cyclic ancestry. Selection retains wallet identity even when names repeat.

**Biến động ví**

A separate section labeled `Biến động ví`, with helper `Gồm chuyển khoản và các khoản vay, trả nợ có chiều tiền đã xác minh.` Use signed daily bars around a zero baseline, faceted by currency and clearly scoped to wallets. Direction labels distinguish inflow/outflow; do not label this net income or balance history. Never draw a historical net-worth curve from imported movements.

**Report context**

Each report includes a compact `Phạm vi dữ liệu` disclosure: represented period, wallet-scoped covered/missing ranges, included/excluded/rejected/unresolved counts by reason. Explain `Phạm vi đã nhập không xác nhận lịch sử đầy đủ từ Money Lover.` Persistent partial warnings stay visible when this disclosure is closed.

On mobile the order is title → period/filters → balance strip → coverage notice → income/spending → category breakdown → wallet movement → scope detail. No analytical card carousel.

### 6.2 Giao dịch: exact read-only explorer

Direct entry defaults to **all imported kinds**, not just ordinary expenses. A drill-down retains its originating report predicates and shows a contextual label such as `Từ Chi tiêu`; changing that scope must be explicit.

**Desktop layout:** title/action row; full-width search plus `Bộ lọc`; wrapping applied-filter chips; scope/quality line; transaction table; bounded pagination controls. Search placeholder: `Tìm ghi chú, đối tác hoặc ID đầy đủ`. Search is case- and Vietnamese-diacritic-insensitive for note/counterparty text; complete source ID equality only. Explain this distinction in helper text.

**Table columns:** `Ngày` (104px), `Giao dịch` (flexible), `Ví / Danh mục` (flexible), `Loại` (128px), `Số tiền` (right-aligned, minimum 168px). Row note occupies at most two lines with full content in detail. Show meaningful issue badges beside the classification, not in a hidden hover state. At intermediate widths move secondary category detail onto the transaction subtitle rather than overflow.

**Filter sheet groups:**

1. `Thời gian`: inclusive accounting dates and supported presets.
2. `Ví và tiền tệ`: wallet multi-select including archived; currency multi-select.
3. `Phân loại`: exact kind/group, one-wallet category subtree, reporting inclusion and quality status.
4. `Số tiền`: inclusive minimum/maximum magnitude, enabled only with one currency.

Amount input is decimal text, not a floating-point numeric stepper. Distinguish report exclusion from `Cần kiểm tra`; missing `exclude_report` is unknown. Valid rows with unresolved relationships may remain classified, so unresolved is not synonymous with unusable.

**Mobile records:** date/group label, transaction note/category, full right-aligned or next-line amount, wallet, kind and issue badges. Preserve exact values at 390px without ellipsis. Entire row may open detail, with an accessible named control. No bulk selection or edit gesture.

**Pagination:** default 50, maximum 100; `Mới nhất` and `Cũ nhất` are server-defined stable order. Show `Trang trước` only when prior cursor state is available and `Trang sau` only when `has_more`. No fabricated total row count, page count or jump-to-page field. Preserve normalized filters in the URL; pagination is not the source of aggregate totals.

On `stale_cursor`, discard cursor history, return to first page and announce `Dữ liệu đã thay đổi. Đã tải lại từ đầu.` Do not append stale and new pages together. Free-text URLs are private-owner navigation, not public share links; do not send financial search strings to analytics.

### 6.3 Transaction detail

Desktop right panel; mobile full-screen. Header `Chi tiết giao dịch`, close/back action and full amount with currency. Below: accounting date, source magnitude/direction explanation, kind, wallet, wallet-scoped category path, reporting inclusion and readiness.

Keep note/counterparty text as readable source evidence. Multiple counterparty labels do not imply multiple copies of the transaction amount. Display complete source ID in a copyable, wrapping monospace field. Copy action confirmation can use a short Sonner toast.

Explain issues in a dedicated visible region: `Chưa tìm thấy giao dịch đối ứng`, `Chưa xác định tiền tệ`, `Chưa phân loại`, or `Cần kiểm tra số tiền`. A missing relationship is not rendered as a link to a nonexistent row. Known owner-authorized related/parent transactions may be links only when provided by the API. Do not fabricate transfer balancing legs or calculate debt balances here.

Separate `Ngày hạch toán` from optional source creation/import timestamps. Do not render raw JSON, remote membership lists, credentials, unverified image references as URLs, unverified reminders or zero coordinates as a map. There are no edit, delete, repayment, reclassification or upload actions.

### 6.4 Ví: observed balances

Use a grouped list, not credit-card mockups. Group by currency; each wallet row contains name, current inclusion state, exact observed balance and observation time. Unknown balance uses `Không rõ`. Long wallet names wrap; opaque source type values do not become invented labels such as bank or credit card.

Default current totals exclude deleted, archived and `exclude_total` wallets. Offer explicit local view controls `Hiện ví lưu trữ` and `Gồm ví bị loại khỏi tổng`. Deleted wallets never enter current totals. These are report filters, not edits to provider flags. Historical spending includes archived-wallet history by default and is not silently changed by these balance controls.

Opening a wallet shows balance observations by currency, timestamps and a scoped transaction link. If observation history is available in a future accepted contract, show it explicitly as observations, not an interpolated historical balance line. The current proposed wallet interface does not authorize inventing a historical-snapshots endpoint.

### 6.5 Đồng bộ: manual control and trustworthy health

This is an operational page, not a settings form with stored credentials. Top region shows connection state and the `Đồng bộ ngay` action or current active-run entry. Below, separate:

- `Lần thử gần nhất`: mode, request/start/finish timestamps and terminal state.
- `Lần thành công gần nhất`: independently stored timestamp; use `Chưa có` until one exists.
- `Phạm vi đã nhập`: wallet/date ranges and missing scopes, not an all-time completion claim.
- `Cần kiểm tra`: sanitized rejected/unresolved counts and explanations.

Use a scope table on desktop and stacked scope records on mobile. Show wallet, scope type/date range, state and fetched/accepted/rejected counts. Common metadata/category/balance/debt scopes remain visible; progress is not merely transaction-window count. No raw provider response, staging payload download or speculative run-history endpoint.

**Fresh-token dialog**

Title `Đồng bộ Money Lover`. Read-only identity context if verified. Mode selection and a labeled password-style field `Token truy cập Money Lover`; reveal toggle with a clear name; helper `Mỗi lần đồng bộ cần token mới. Token không được lưu để dùng lại.` Submit `Bắt đầu đồng bộ`; secondary `Hủy` closes entry without submitting.

Do not promise that tokens never leave memory: the backend uses a short-lived one-time Redis handoff. Never persist token input in localStorage, sessionStorage, URL, analytics, logs, error reports or retained query/mutation caches. Clear transient field and request state immediately after submission/close; avoid automatic mutation retries or logging secret variables. Only authenticated HTTPS CashLens receives it, never Money Lover directly from the browser.

**Mode labels and eligibility**

| API concept | Vietnamese UI | Visible explanation |
| --- | --- | --- |
| Full | `Toàn bộ từ 01/2020` | Mandatory initially; monthly windows through today, newest first; not an all-time completeness guarantee |
| 90-day | `90 ngày gần đây` | Default only after a succeeded Full run; rolling 90 calendar days through today |
| Quick | `Nhanh` | Available after a successful run; overlaps one day with last-success calendar date; can miss backdated entries and older changes |

Every mode refreshes metadata, categories, balance observations and debt evidence. Explain this once below the selector. Older changes may remain stale until a broader explicit run; no fixed automatic refresh SLA or scheduled reconciliation promise.

Use server-provided eligibility. Do not permit Quick/90-day by visually enabling them based merely on local history. Same identity reconnects; identity mismatch blocks before financial writes and has no `Switch account anyway` action.

**Progress and lifecycle**

| State | Label | Presentation and action |
| --- | --- | --- |
| `queued` | `Đang chờ` | Static queue icon, request time; no fake progress percentage |
| `running` | `Đang đồng bộ` | Completed/remaining scopes and diagnostic counts; `Ẩn tiến trình`, `Dừng đồng bộ` |
| `succeeded` | `Đã hoàn tất phạm vi yêu cầu` | Success confirmation plus explicit requested range; no claim of provider completeness |
| `partial` | `Hoàn tất một phần` | Warning, accepted scope summary, failed/rejected detail; fresh-token retry |
| `failed` | `Đồng bộ thất bại` | Sanitized reason, no claim of financial publication; fresh-token retry |
| `cancelled` | `Đã dừng` | Retained committed scopes and stopping time |
| `auth_required` connection | `Cần token mới` | Explain rejected/expired token separately from run outcome; retained data stays available |

Progress is numeric only when the server supplies a meaningful known scope denominator. A progress bar then denotes **requested scope progress**, never percent of the owner's financial history. Otherwise show phase and counts without a percentage.

Hiding progress leaves a global labeled active indicator in the header and the `Đồng bộ` destination. Re-entering `Đồng bộ ngay` while queued/running opens the existing run; it does not ask for another token or start competing work.

`Dừng đồng bộ` opens a short confirmation: `Dữ liệu đã nhập sẽ được giữ lại. Tác vụ sẽ dừng ở điểm an toàn tiếp theo.` Confirmation enters `Đang yêu cầu dừng`, not immediate cancelled success. Retry after a terminal outcome is a new run with a fresh token; it can recover failed/missing transaction scopes while refreshing common scopes.

Poll relevant active CashLens run status only; stop on terminal state. Reflect committed financial revisions without disrupting current reading, invalidate financial queries as required and handle stale pagination explicitly. No SSE, WebSocket or background provider calls.

---

## 7. Data Visualization and Financial Truth

### Chart construction

- Recharts renders the accepted server series. Do not derive sums, comparison deltas, category rollups or signed movement from raw rows in React.
- Income uses teal solid columns; spending uses graphite/silver with an additional distinguishable outline or hatch. Legends use labels and swatches, never color alone.
- Category rank uses neutral horizontal bars with teal only for active selection. Cash movement uses above/below-zero position and direction labels, not red/green sentiment.
- Use a zero baseline for magnitude bars. Time axes show actual accounting buckets; gaps in missing coverage are not fabricated zeros. Never smooth over unknown periods or interpolate observations as verified history.
- Plot axes use 12px type, sparse gridlines, units and currency. Minimize visual noise without removing scale context. No 3D, donut centerpiece, chart gradients or decorative sparklines beside every amount.
- Exact tooltips include period, currency, kind/series, precise total and a named drill-down. Tooltips work on focus/tap as well as hover, stay within the viewport and are not the only way to read values.
- All chart controls are Vietnamese, including the accessible chart-table disclosure `Xem bảng dữ liệu`.
- Recharts numeric coordinates are an explicit rendering boundary, not the monetary source of truth. If numeric plotting is necessary, use a reviewed bounded/scaled adapter or backend-provided plot coordinates, retain original decimal strings for labels/evidence and never reuse plot numbers for arithmetic. If a value cannot be plotted safely, render the exact accessible data table instead of silently coercing it.

### Non-negotiable distinctions

| Concept | Meaning | Must not imply |
| --- | --- | --- |
| `Thu nhập & chi tiêu` | Ready, non-deleted ordinary income/expense, known currency, explicitly report-included | All wallet inflows/outflows |
| `Thu nhập ròng` | Server income minus ordinary spending | Wallet balance change |
| `Biến động ví` | Verified signed movement including transfers/debt movements and source-report-excluded rows | Spending or a second debt ledger |
| `Số dư ghi nhận` | Latest observed wallet/currency balance with observation time | Live, end-of-day or reconstructed balance |
| `Phạm vi đã nhập` | Represented attempted wallet/date scopes and quality | Authoritative complete provider history |
| `Lần thành công gần nhất` | Last succeeded required run | Last attempt, continuous freshness or complete history |

Unknown currency is searchable and explained but excluded from currency totals. Unknown semantics do not become spending based on name or amount. Valid zero magnitudes remain visible. Unexpected negative transaction magnitudes need review; negative wallet observations may be valid. Missing category ancestry can coexist with otherwise valid spending. Transfer legs remain independent and cross-currency values never imply equal nominal amounts or automatic cancellation.

One overview response must provide a coherent dataset revision across its sections. UI warnings and displayed totals should come from that same context, not separately combined old/new queries. Coverage is per wallet and accounting range; do not substitute a single reassuring green badge.

---

## 8. Motion & Interaction

Motion exists only to explain a state transition or acknowledge input. Stable financial content mounts without staggered reveals. Numbers do not roll, cards do not float, and active sync badges do not pulse indefinitely.

| Interaction | Duration | Behavior |
| --- | --- | --- |
| Button hover/press | 100ms | Fill change; optional 1px downward press |
| Popover/dialog | 140ms | Opacity and at most 4px translation |
| Desktop detail/mobile sheet | 180ms | Short edge translation plus opacity |
| Selection or notice update | 120ms | Color/opacity feedback without moving rows |
| Reduced motion | 0ms | Immediate stable state with all feedback text retained |

Use `cubic-bezier(0.2, 0, 0, 1)`, not bouncy spring physics. The low-motion product context intentionally overrides the generic Stitch spring/loop baseline. Implement using CSS and existing `tw-animate-css`; no new Motion or GSAP dependency is justified.

Animate only transform and opacity. Do not animate dimensions, chart values, table order or layout on sync polling. Use `will-change` only during actual transitions. Respect `prefers-reduced-motion` for all motion, regardless of dial value. Avoid `transition: all`, scroll listeners and React-state animation loops.

Use a polite live region for meaningful run-phase changes, cancellation outcome and stale-cursor recovery. Do not announce every polled count. Use `aria-busy` on the affected loading region while preserving navigable surrounding content.

---

## 9. Accessibility, Copy and Privacy

- Target WCAG 2.2 AA. Set document language to Vietnamese. Provide semantic landmarks, one page H1, skip-to-content, named navigation and `aria-current`.
- Every primary action is keyboard-reachable. Tables have associated headers and sortable controls with state; mobile lists preserve equivalent information. A clickable row is not an inaccessible pointer-only container.
- Visible focus is not clipped by sticky headers or overlay boundaries. Dialog close returns focus to the triggering row/action; full-screen detail has a reliable back action.
- Maintain 44px touch targets and readable 16px mobile form text. Support text zoom, wrapped badges, long names, large exact amounts and OS contrast settings. No custom cursor or gesture-only controls.
- Truncated notes may have tooltips, but complete note/category/wallet text is available in detail without hover. IDs can wrap with `overflow-wrap: anywhere`; never truncate the only available exact ID.
- Use factual Vietnamese. Prefer `Dữ liệu chưa đầy đủ`, `Chưa xác định tiền tệ`, `Không tải được dữ liệu`, `Xem giao dịch`. Avoid boastful claims, moral judgments about spending and fabricated advice.
- Standard kind labels: `Thu nhập`, `Chi tiêu`, `Chuyển vào`, `Chuyển ra`, `Cho vay`, `Đi vay`, `Trả nợ`, `Thu hồi nợ`, `Chưa phân loại`. Display backend classification, never infer it from translated names.
- No remote private samples, raw evidence, exposed tokens or personal counterparty names enter design assets or browser fixtures. Use explicitly marked synthetic design content. Zero is allowed as real data; do not fake attractive numbers or precision to decorate a screen.
- No public sharing, analytics capture of financial notes/search queries, token screenshots or remote membership-derived access controls. URL filters do not authorize access; every read remains owner-scoped server-side.
- Missing and inaccessible resources share an indistinguishable not-found treatment. Do not reveal that another owner has a requested wallet/transaction/run.
- Do not add recurring backup warnings: issue #9 requires launch-risk acknowledgement, not persistent dashboard clutter.

---

## 10. Stitch Screen-Generation Handoff

### Global prompt contract

> Design CashLens, a private Vietnamese read-only Money Lover analysis workspace. Follow DESIGN.md exactly. Use Geist, zinc-neutral surfaces and one deep-teal action accent, flat 12px panels, 44px controls and precise right-aligned tabular financial figures. Desktop has a persistent sidebar with Tổng quan, Giao dịch, Đồng bộ, Ví. Mobile has those four labeled bottom-navigation destinations, single-column content, visible search/filter chips and full-screen transaction detail. Prioritize spending analysis over compact timestamped observed balances. Show financial uncertainty explicitly. No banking-card mockups, hero, photography, gradients, neon, perpetual motion, write-back controls or mixed-currency totals. All visible copy is Vietnamese except proper names, IDs and currency codes. Values in concepts are labeled synthetic design data, not actual imported owner data.

### Required screen set

Generate independent, readable screens rather than one tiny multi-screen board. These are generation instructions, not a claim that images or screens have been produced.

| Screen | Desktop 1440×900 | Mobile 390×844 | Required distinguishing state |
| --- | --- | --- | --- |
| Overview | Sidebar, compact balances, 8:4 analytical split | Bottom nav, stacked report sections | Populated analysis with comparison disclosure and partial-coverage notice |
| Explorer | Filtered table and selected-row detail panel | Search, wrapped chips, stacked rows; separate full-screen detail | All-kind rows including transfer and unclassified evidence |
| Filters | Anchored control/sheet with grouped filters | Full-width bottom sheet | Explain one-wallet category and one-currency amount constraints |
| Wallets | Currency-grouped observation rows | Stacked wallets and observation context | One missing observation shown as `Không rõ`; archived/excluded filters |
| Sync entry | 480px fresh-token dialog over health page | Keyboard-safe dialog/sheet | Full first-run eligibility; no saved token |
| Active sync | Requested-scope progress and retained analysis context | Compact global indicator and reopenable progress | Hidden/reopened run, stop confirmation, no fake percentage |
| Sync recovery | Sanitized partial-run scopes and last-success distinction | Stacked scope diagnostics | Auth-required state with prior accepted data retained |
| First import | Empty analytical structure and single next action | Compact empty guidance above bottom nav | No fake zero totals |
| Read failure | Affected region error with retry | Same region-level treatment | Distinguish CashLens read failure from provider run failure |

Include dark counterparts for overview, explorer/detail and token/health surfaces to verify palette parity. Include skeleton, valid empty-filter, stale-cursor notice and known-zero variations as component states. Do not let synthetic screen content become an invented MSW schema; browser fixtures must later follow implemented OpenAPI.

---

## 11. Implementation and Acceptance Checklist

### Implementation boundaries

- Keep React 19 + TypeScript Vite SPA. No Next.js, React Server Components or `use client` scaffolding.
- Use installed Tailwind v4, source-owned Base UI shadcn components, Lucide, Recharts, TanStack Table, React Hook Form/Zod and Sonner. Do not mix in Radix, Fluent or Carbon themes merely to imitate another design system.
- Router owns normalized shareable filters; Query owns server data; dialog/detail draft state stays local. No new Zustand or handwritten parallel financial client.
- Generate Fetch/React Query APIs with Orval only from implemented FastAPI OpenAPI. Never edit generated files or route trees by hand. The proposed `/api/v0` status/sync, finance and overview interfaces in issue #9 bound the design; this document adds none.
- Financial decimal strings and bigint IDs stay exact. Business aggregation, classification, comparison boundaries, drill-down predicates and authorization belong to the backend.
- Add font assets and semantic tokens before screens. Build shell and primitives once; compose feature-owned overview, explorer, wallet and sync components without duplicating filter/status semantics.
- No live provider access is authorized by a screen design. No UI completion or mock success waives provider-evidence, accounting or launch gates.

### Visual and interaction acceptance

- [ ] 1440×900: title, filters, compact balances and main analysis plot are visible without a marketing-sized header.
- [ ] 390×844: primary actions, bottom navigation, search/chips and sheet close/apply controls are usable with no horizontal overflow.
- [ ] 320px width, 200% text zoom, long Vietnamese names and large exact amounts do not hide money or actions.
- [ ] Light and dark modes preserve text/control contrast, chart distinctions, warnings and focus indicators.
- [ ] All controls have keyboard behavior, visible focus, accessible names and 44px touch targets.
- [ ] Source/read error, provider error, no data, no matching rows, unknown value and known zero look and read differently.
- [ ] Observed balances include per-wallet observation context; they are never presented as live or historical net worth.
- [ ] Multiple currencies remain separate in cards, axes, categories, details and comparisons.
- [ ] Archived/excluded balance filters do not silently change historical spending eligibility.
- [ ] Every chart/metric drill-down preserves exact server report predicates and URL state.
- [ ] Unknown semantics, missing currency and unresolved relationships have visible explanations, not only dim text.
- [ ] Full/90-day/Quick eligibility, fresh-token entry, active-run reuse, hide/reopen, safe cancellation and fresh-token recovery follow issue #9.
- [ ] Token values never persist in browser storage, debug output, URLs, fixtures or retained mutation state.
- [ ] Last attempt, last success, mode, attempted coverage and quality counts are distinct.
- [ ] New dataset revisions trigger coherent refresh/stale-cursor recovery, not mixed or silently appended history.
- [ ] Motion is brief, motivated and disabled under reduced motion; charts and financial figures do not animate on polling.
- [ ] No fake totals, raw private samples, forbidden write actions, invented API calls or provider completeness claims.

When implementation exists, run the `web/AGENTS.md` build, lint, formatting, Vitest and Playwright checks from `web/` with pnpm. Validate current stable Chromium at the two required viewports, keyboard navigation, both themes and all degraded states. UI tests do not prove accounting correctness or owner isolation; retain issue #9's PostgreSQL-backed integration and provider-evidence gates. This document is a design specification, not a test-pass or production-readiness report.

---

## 12. Anti-Patterns: Never Do

- No oversized hero, inline-photo headline, marketing feature grid, testimonials or stock-image decoration in the financial workspace.
- No Inter default, serif display, uppercase eyebrow above every panel, emojis or fake account avatars.
- No purple/neon glow, gradient text, glass surfaces, pure-black canvas or inconsistent warm/cool gray palettes.
- No three identical KPI cards dominating the page; compact balances and analytical hierarchy come first.
- No nested card stacks, giant pill buttons, gratuitous shadows or decorative grid lines.
- No perpetual pulses, shimmering every row, waterfall transaction entrances, scroll hijacking or counter animations.
- No unlabeled chart color, red spending-as-error convention, arbitrary percentage badges or fabricated chart data.
- No assumed full history, transient zero balances, mixed-currency totals, local arithmetic or synthetic transfer/debt counterparts.
- No stored provider credentials, auto-sync switches, scheduled refresh controls, account-replacement bypass or browser-to-provider requests.
- No transaction editing, add-expense action, payment instruction, debt-balance dashboard or invented net-worth reporting.
- No hidden mobile filters, compressed overflowing table, clipped amounts, hover-only evidence or gesture-only detail navigation.
- No English starter actions, artificial marketing promises, generic placeholder identities or unmarked synthetic finance data.
