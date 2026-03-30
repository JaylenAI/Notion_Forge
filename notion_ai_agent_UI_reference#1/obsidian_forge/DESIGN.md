# Design System Specification: The Obsidian Blueprint

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Alchemist"**

This design system is built to bridge the gap between high-utility developer tools and the "magical" intuition of AI. It rejects the clinical, flat aesthetics of standard SaaS in favor of **The Digital Alchemist**—a philosophy that treats the UI as a series of deep, obsidian-layered surfaces illuminated by "magical" light sources.

We break the "template" look by avoiding rigid, boxed-in grids. Instead, we use **intentional asymmetry**, where AI-generated content flows through floating glass modules. We prioritize tonal depth over structural lines, creating an interface that feels like a high-end physical workspace illuminated by neon accents.

---

## 2. Colors & Surface Philosophy

### The Tonal Palette
The foundation is a "Deep Dark" architecture. We do not use pure black for everything; we use a hierarchy of charcoals to define importance.

*   **Core Background:** `surface` (#131313) — The infinite canvas.
*   **Primary Action:** `primary` (#adc6ff) — Electric Blue. Used for the "Spark" of AI interaction.
*   **Warmth/Humanity:** `secondary` (#ffb59a) — Sunset Orange. References the familiar warmth of the Notion workspace.
*   **Success/Growth:** `tertiary` (#4edea3) — Emerald Green. For completed builds and active states.

### The "No-Line" Rule
**Explicit Instruction:** Do not use `1px` solid borders for sectioning. Traditional dividers are forbidden.
*   **Boundaries:** Define edges solely through background shifts. Place a `surface_container_high` module on top of a `surface_container_low` background. 
*   **The "Glass & Gradient" Rule:** Floating elements (like AI chat bubbles or tooltips) must use glassmorphism. Use `surface_variant` at 60% opacity with a `20px` backdrop-blur. 
*   **Signature Textures:** For primary CTAs, use a linear gradient from `primary_container` (#006de6) to `primary` (#adc6ff) at a 135-degree angle to provide a "glowing" depth.

---

## 3. Typography: Editorial Authority

We pair **Manrope** (Display/Headlines) with **Inter** (Body/UI) to create a balance between "Editorial Premium" and "Developer Logic."

*   **Display (Manrope):** High-contrast, tight letter spacing (-0.02em). Used for hero moments where the AI "speaks" its primary vision.
*   **Body (Inter):** Highly legible, standard weight for technical logs and template data.
*   **Hierarchy as Identity:** Use `display-md` for AI headers and `label-sm` (uppercase, tracked out +10%) for technical metadata. This contrast signals that the system is both "smart" and "precise."

---

## 4. Elevation & Depth: Tonal Layering

We move away from the "shadow-only" approach to a **Layering Principle**.

### The Layering Stack
1.  **Base Layer:** `surface_container_lowest` (#0e0e0e) — For deep sidebars.
2.  **App Floor:** `surface` (#131313) — The main workspace.
3.  **Raised Cards:** `surface_container_low` (#1c1b1b).
4.  **Interactive Elements:** `surface_container_highest` (#353534).

### Ambient Shadows & Ghost Borders
*   **Ambient Shadows:** For floating glass panels, use a shadow with a `48px` blur, `0px` spread, and 6% opacity, tinted with `primary` (#adc6ff). This mimics the blue "glow" of the AI light source.
*   **The "Ghost Border" Fallback:** If accessibility requires a border, use `outline_variant` (#424656) at **15% opacity**. It should be felt, not seen.

---

## 5. Components: The Alchemist’s Tools

### Sophisticated Chat Bubbles
*   **AI Side:** Glassmorphic container (`surface_variant` at 40% opacity) with a `primary` glow on the left edge. No hard borders.
*   **User Side:** `surface_container_high` with `on_surface_variant` text.
*   **Spacing:** Use `spacing-4` (1rem) internal padding.

### Real-Time Progress Cards
*   **Construction:** Use `surface_container_low` as the base. 
*   **The Blueprint Effect:** Use a subtle background pattern of `outline_variant` dots (2px apart) to signify "work in progress." 
*   **Progress Bar:** A `2px` height line using `tertiary` (#4edea3) with a `4px` glow.

### Blueprint Tree Visualizations
*   **Nodes:** Use `md` (0.375rem) roundedness. 
*   **Connectors:** Use `outline_variant` at 30% opacity. 
*   **Interactivity:** On hover, the node should transition from `surface_container` to `primary_container` over `300ms`.

### Integration Forms
*   **Input Fields:** No background. Use a bottom-only `Ghost Border`. On focus, the border transitions to 100% opacity `primary` with a subtle `primary_fixed_dim` outer glow.
*   **Validation:** Use `error` (#ffb4ab) only for text; icons should use `secondary` to maintain the "warmth" of the brand.

---

## 6. Do's and Don'ts

### Do
*   **Do** use asymmetrical layouts. Let cards overlap slightly to create depth.
*   **Do** use the `24` (6rem) spacing for major section breathing room.
*   **Do** rely on `surface_bright` for subtle hover states rather than changing the border color.
*   **Do** use `rounded-xl` (0.75rem) for main containers to soften the "tech" feel.

### Don't
*   **Don't** use 100% white (#FFFFFF). Always use `on_surface` (#e5e2e1) to protect the user's eyes in deep dark mode.
*   **Don't** use "Drop Shadows" that are black. Shadows must be ambient and tinted by the UI’s primary accent.
*   **Don't** use divider lines between list items. Use `spacing-2` (0.5rem) of vertical whitespace or a `surface_container_low` background on alternate items.
*   **Don't** use standard "Success Green." Use the specified `tertiary` Emerald for a more premium, "gemstone" feel.