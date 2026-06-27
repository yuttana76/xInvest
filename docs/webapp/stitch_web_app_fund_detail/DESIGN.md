```markdown
# Design System Strategy: The Sovereign Ledger

## 1. Overview & Creative North Star
The design system for this investment dashboard is built upon the **"Sovereign Ledger"** creative north star. In high-end fund management, luxury is not defined by excess, but by the precision of information and the elegance of the void (whitespace). 

This system rejects the "boxed-in" nature of traditional fintech templates. Instead, it adopts an **Editorial Financial** aesthetic—utilizing high-contrast typography scales, intentional asymmetry, and a sense of architectural layering. By moving away from rigid lines and toward tonal depth, we create a digital environment that feels as authoritative as a printed quarterly report and as fluid as a modern trading floor.

## 2. Color Theory & Tonal Architecture
The palette centers on deep, institutional blues and teals, punctuated by a sophisticated "Safety Orange" for growth and action.

### The "No-Line" Rule
To achieve a premium, custom feel, **1px solid borders are prohibited** for sectioning or containment. Boundaries must be defined through:
*   **Background Shifts:** Distinguishing a `surface-container-low` section from a `surface` background.
*   **Tonal Transitions:** Using subtle shifts in lightness to imply structure without the "clutter" of lines.

### Surface Hierarchy & Nesting
Hierarchy is established through physical layering, mimicking stacked sheets of fine, semi-translucent paper.
*   **Level 0 (Base):** `surface` (#fbf9f8) – The canvas.
*   **Level 1 (Sub-sections):** `surface-container-low` (#f6f3f2) – Large structural areas.
*   **Level 2 (Cards/Modules):** `surface-container-lowest` (#ffffff) – Used for primary data containers to make them "pop" against the off-white base.
*   **Level 3 (Interactive/Active):** `surface-container-highest` (#e4e2e1) – Reserved for hover states or active selection backgrounds.

### Glass & Gradient Signature
*   **Glassmorphism:** Use `surface-container-lowest` with 80% opacity and a `20px` backdrop-blur for floating navigation or modal overlays. This integrates the UI rather than siloing it.
*   **The Power Gradient:** For high-value actions (e.g., "Invest Now"), use a linear gradient from `primary` (#003b93) to `primary_container` (#0051c3) at a 135-degree angle. This adds a "soul" and depth that flat color cannot replicate.

## 3. Typography: The Editorial Voice
The typography system balances the architectural strength of **Manrope** for display elements with the utilitarian clarity of **Inter** for data density.

*   **Display (Manrope):** Large, bold headlines for Portfolio Values and Fund Names. The wide tracking and geometric shapes convey stability.
*   **Body (Inter):** Optimized for financial legibility. The high x-height ensures that complex figures remain readable at small sizes.
*   **Data Monospace (Fallback):** For fluctuating tickers or transaction IDs, use a monospace font to ensure numerical alignment.

**Hierarchy Note:** Always lead with size contrast. A `display-lg` portfolio balance should be paired with a much smaller `label-md` "Total Assets" tag to create an editorial, high-end feel.

## 4. Elevation & Depth
Depth is a functional tool, not a decoration. We use **Tonal Layering** to guide the eye.

*   **The Layering Principle:** Avoid shadows where background color shifts can do the work. A `surface-container-lowest` card sitting on a `surface-container-low` background creates a natural, soft lift.
*   **Ambient Shadows:** For floating elements (modals, dropdowns), use "Airy Shadows."
    *   *Blur:* 32px to 64px.
    *   *Opacity:* 4-6% of the `on_surface` color.
    *   *Purpose:* To mimic natural light diffusion, avoiding the "dirty" look of standard grey shadows.
*   **The "Ghost Border":** If accessibility requires a stroke (e.g., in high-contrast modes), use `outline_variant` at **15% opacity**. It should be felt, not seen.

## 5. Components

### Buttons (The Action Signature)
*   **Primary:** Gradient of `primary` to `primary_container`, `DEFAULT` (8px) roundness, white text. No border.
*   **Secondary:** `surface_container_highest` background with `on_surface` text.
*   **Tertiary:** Transparent background with `primary` text. Use for low-emphasis actions like "View More."

### Data Cards & Lists
*   **Rule:** Forbid divider lines. 
*   **Separation:** Use `8px` to `16px` of vertical whitespace (from the Spacing Scale) or a subtle shift to `surface_container_low`.
*   **Metrics:** Hero metrics (e.g., +12.5% ROI) should use `secondary` (#964900) or a vibrant teal if growth is positive, rendered in `headline-lg` to prioritize the "Data-Rich" requirement.

### Input Fields
*   **Style:** Minimalist. Only a bottom-border using `outline_variant` at 30% opacity. 
*   **Focus State:** Transition the bottom-border to `primary` and add a subtle `surface_tint` glow.
*   **Thai Support:** Ensure line-height for `body-md` is increased to 1.6x to accommodate Sarabun or other Thai character ascenders/descenders without clipping.

### Selection Chips
*   **Visuals:** Use `md` (12px) rounding. Unselected chips should be `surface_container_high`. Selected chips move to `primary` with `on_primary` text.

### Interactive Charts
*   **Aesthetic:** Use `primary` for the main trend line. Fill the area below with a gradient of `primary` (20% opacity) fading to transparent. Use `secondary_container` for "Callout" points on the chart to highlight peak performance.

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts (e.g., a wide left column for charts and a narrow right column for transaction history) to break the "grid" feel.
*   **Do** prioritize `body-lg` for primary financial figures; money should always be easy to read.
*   **Do** use `surface_container_lowest` for the most important interactive cards to create a "raised" effect.

### Don't
*   **Don't** use 100% black text. Use `on_surface` (#1b1c1c) for a softer, more professional contrast.
*   **Don't** use standard "Success Green" (#008000). Use the system’s teals or `primary_container` hues to maintain the sophisticated palette.
*   **Don't** crowd the edges. If a container feels full, add another 8px of padding. In this system, whitespace is a sign of premium quality.
*   **Don't** use 1px dividers between list items. Use the rhythm of the typography and vertical spacing to define rows.

---
*Director's Final Note: The goal is to make the investor feel like they are looking at a private bank's bespoke terminal. Every pixel must feel intentional, and every piece of data must have room to breathe.*```