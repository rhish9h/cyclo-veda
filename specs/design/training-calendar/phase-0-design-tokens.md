# Phase 0 — Design Token Foundation

**Prerequisite for all subsequent phases.**

---

## Goal

Establish a single source of truth for all visual values in `src/index.css` before any
calendar component is written. Every `.module.css` file — existing and new — will reference
tokens via `var(--token-name)`. No raw hex values or colour literals in component CSS.

---

## Why Now

A scan of the existing five `.module.css` files found **90 hardcoded colour values**, and the
inconsistency is already visible:

- `Login.module.css` uses indigo `#6366f1` as the brand/primary colour
- `Layout.module.css` uses blue `#007bff` for the active nav item

The calendar will add ~10 new components. Without a token layer, the drift compounds and a
future design update requires hunting through every file individually.

**Resolution**: indigo (`#6366f1`) is adopted as `--color-primary` across the entire app,
replacing the blue in Layout.

---

## Token File: `src/index.css`

Tokens are added inside the existing `:root` block, **above** the current typography and
rendering settings. Two layers: primitive → semantic.

### Primitive Tokens

Raw palette values with no UI context implied.

```css
/* --- Colour Primitives --- */

/* Brand */
--color-indigo-400: #818cf8;
--color-indigo-500: #6366f1;
--color-indigo-600: #4f46e5;
--color-violet-500: #8b5cf6;

/* Neutrals */
--color-neutral-0:   #ffffff;
--color-neutral-50:  #f8f9fa;
--color-neutral-100: #e9ecef;
--color-neutral-200: #dee2e6;
--color-neutral-300: #6c757d;
--color-neutral-400: #495057;
--color-neutral-500: #374151;
--color-neutral-600: #1f2937;
--color-neutral-900: #1a1a1a;

/* Feedback */
--color-red-500:    #dc2626;
--color-red-600:    #dc3545;
--color-orange-400: #fb923c;

/* --- Spacing Scale --- */
--space-1:  0.25rem;   /*  4px */
--space-2:  0.5rem;    /*  8px */
--space-3:  0.75rem;   /* 12px */
--space-4:  1rem;      /* 16px */
--space-6:  1.5rem;    /* 24px */
--space-8:  2rem;      /* 32px */
--space-10: 2.5rem;    /* 40px */
--space-12: 3rem;      /* 48px */

/* --- Border Radius Scale --- */
--radius-sm:   6px;
--radius-md:   8px;
--radius-lg:   12px;
--radius-xl:   20px;
--radius-full: 9999px;

/* --- Typography Scale --- */
--font-size-xs:   0.75rem;    /* 12px */
--font-size-sm:   0.875rem;   /* 14px */
--font-size-base: 1rem;       /* 16px */
--font-size-lg:   1.125rem;   /* 18px */
--font-size-xl:   1.25rem;    /* 20px */
--font-size-2xl:  1.5rem;     /* 24px */
--font-size-3xl:  1.875rem;   /* 30px */

/* --- Shadow Scale --- */
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md: 0 2px 4px rgba(0, 0, 0, 0.10);
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.08);
--shadow-xl: 0 32px 64px rgba(0, 0, 0, 0.12);
```

### Semantic Tokens

Map primitives to UI roles. These are what component CSS files reference.

```css
/* --- Brand / Primary Actions --- */
--color-primary:        var(--color-indigo-500);
--color-primary-hover:  var(--color-indigo-600);
--color-primary-subtle: #e3f2fd;   /* active nav background */
--color-primary-ring:   rgba(99, 102, 241, 0.15);

/* --- Surfaces --- */
--color-surface:        var(--color-neutral-0);
--color-surface-subtle: var(--color-neutral-50);
--color-border:         var(--color-neutral-100);

/* --- Text --- */
--color-text-primary:   var(--color-neutral-900);
--color-text-secondary: var(--color-neutral-300);
--color-text-muted:     var(--color-neutral-400);
--color-text-label:     var(--color-neutral-500);

/* --- Feedback --- */
--color-danger:       var(--color-red-500);
--color-danger-hover: var(--color-red-600);

/* --- Calendar (used from Phase 1 onwards) --- */
--color-strava:           var(--color-orange-400);
--color-planned-workout:  var(--color-primary);
```

---

## Deliverables

| File | Change |
|------|--------|
| `src/index.css` | Add primitive + semantic token blocks inside `:root`, above existing typography settings |
| `src/components/layout/Layout/Layout.module.css` | Replace all hardcoded values. Unify nav active colour to `--color-primary` (was `#1976d2` / `#007bff`) |
| `src/components/auth/Login.module.css` | Replace all hardcoded values with token references |
| `src/components/layout/Settings/Settings.module.css` | Replace all hardcoded values |
| `src/components/layout/Settings/ConnectionCard/ConnectionCard.module.css` | Replace all hardcoded values |
| `src/components/layout/Dashboard/Dashboard.module.css` | Replace all hardcoded values |

---

## Definition of Done

- Zero raw hex values (`#xxxxxx`) or raw colour `rgba()` literals remain in any `.module.css` file
  - Exception: `rgba(0, 0, 0, …)` inside shadow definitions may remain as shadow tokens cover these
- App is **visually identical** before and after — this is a pure refactor, no visual changes
- Brand colour is unified: `--color-primary` (indigo `#6366f1`) used for Login button, Layout nav active state, and all other primary interactive elements
- No new components or features are introduced in this phase
