# Design System Strategy: The Architectural Workspace

## 1. Overview & Creative North Star
**Creative North Star: The Living Document**

This design system is not merely a collection of UI components; it is an architectural framework for thought. Inspired by the clarity and modularity of high-end editorial tools, the system treats every interface as a canvas for structured data. We move beyond "template" looks by prioritizing **intentional asymmetry** and **tonal depth** over rigid grid lines. 

The aesthetic is rooted in "Soft Minimalism"—an environment that feels invisible until needed. We break the monotony of standard SaaS layouts by using high-contrast typography scales and overlapping surface layers that suggest a physical workspace of stacked paper and glass.

---

## 2. Colors & Surface Logic
The palette is built on a foundation of sophisticated neutrals, moving away from pure digital blacks and whites toward warmer, more natural tones.

### The "No-Line" Rule
**Explicit Instruction:** Do not use 1px solid borders to section off large areas of the UI. Separation must be achieved through background shifts. For example, a sidebar should be defined by the `surface-container-low` (#f9f3e7) token against a `surface` (#fef9ef) main stage. 

### Surface Hierarchy & Nesting
Treat the UI as a series of nested physical layers. 
- **Base Layer:** `surface` (#fef9ef)
- **Primary Content Area:** `surface-container-lowest` (#ffffff) for maximum focus.
- **Supportive UI (Sidebar/Navigation):** `surface-container-low` (#f9f3e7).
- **Interactive Modals/Popovers:** `surface-container-highest` (#e9e2ce) to create immediate visual gravity.

### Signature Textures
- **The Glass Rule:** For floating menus or "Command Palette" components, use semi-transparent variations of `surface-container` with a `24px` backdrop blur. This allows content to "bleed through," softening the interface.
- **Tonal CTAs:** Instead of flat blocks, use a subtle linear gradient for primary buttons, transitioning from `primary` (#005fad) to `primary_dim` (#005398) at a 145-degree angle. This adds a "soul" to the component that flat color lacks.

---

## 3. Typography
We use **Inter** as our typographic anchor. It is a typeface designed for screens, providing maximum legibility at small sizes and an authoritative, editorial feel at large scales.

- **Display & Headline:** Use `display-md` (2.75rem) for page titles. The tighter tracking and substantial scale convey the "Brand as Editor" identity.
- **Body & Titles:** `body-md` (0.875rem) is our workhorse. We utilize `on_surface_variant` (#635f4f) for secondary body text to reduce eye strain and establish hierarchy without changing font size.
- **Labels:** `label-sm` (0.6875rem) should always be in All Caps with a `+0.05em` letter spacing to denote metadata or "tags."

---

## 4. Elevation & Depth
Depth is a functional tool, not a decoration. We convey hierarchy through **Tonal Layering** rather than traditional drop shadows.

- **The Layering Principle:** To lift a card, place a `surface-container-lowest` (#ffffff) element on top of a `surface-container-low` (#f9f3e7) background. The 1% shift in value creates a "soft lift" that feels premium and architectural.
- **Ambient Shadows:** When a true floating state is required (e.g., a dragged block), use an extra-diffused shadow: `box-shadow: 0 12px 32px rgba(54, 50, 37, 0.08)`. Notice the shadow color uses a tint of `on_surface` (#363225) rather than pure black.
- **The "Ghost Border":** If accessibility requires a border, use the `outline_variant` (#b8b29f) at **15% opacity**. High-contrast, 100% opaque borders are strictly forbidden.

---

## 5. Components

### Block-Based Layouts
Content is moved in "blocks." Each block should have a hover state using `surface_container_high` (#eee8d6) with a `DEFAULT` (0.25rem) corner radius.

### Buttons & Chips
- **Primary:** Gradient fill (Primary to Primary Dim), 4px radius, white text.
- **Secondary:** Transparent background with a "Ghost Border."
- **Chips:** Use `secondary_container` (#e7e2d9) with `label-md` text. Forbid the use of icons in chips unless they represent a specific person or status.

### The Sidebar
A monolithic `surface-container-low` area. Navigation items use `title-sm` typography. Active states are indicated by a background shift to `surface-container-highest`, never a high-contrast color bar.

### Callout Boxes
Use `tertiary_container` (#ddddfe) for informational callouts. The edge should be sharp (`sm` - 2px) to maintain the "native" workspace aesthetic.

### Tables & Galleries
Forbid divider lines. Use `surface-container-low` for header rows and `surface` for body rows. Vertical white space (Spacing `4` - 1rem) is the primary method of separation.

---

## 6. Do's and Don'ts

### Do
- **Use White Space as a Tool:** Use the `8` (2rem) and `12` (3rem) spacing scales to let high-level sections breathe.
- **Layer Surfaces:** Always think "Is this piece of content 'above' or 'inside' the background?" and choose your surface token accordingly.
- **Keep Corners Subtle:** Stick to `sm` (2px) for structural elements and `DEFAULT` (4px) for interactive elements.

### Don't
- **Don't use 1px Dividers:** They clutter the UI. Use a tonal background shift or `1.5` (0.375rem) of vertical space instead.
- **Don't use Pure Black Shadows:** They look "muddy." Always tint your shadows with the `on_surface` color.
- **Don't Over-round:** Avoid the `full` or `xl` radius scales for anything other than specific circular avatars. The workspace must feel "constructed," not "molded."