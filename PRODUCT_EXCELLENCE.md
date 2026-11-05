# AURA Studio v2.1 – Product Excellence Guide

## Philosophy

AURA is a premium product. Every interaction should feel as polished as Linear, Figma, Notion, and Vercel. We focus on refinement, not new features.

## Design System

### Spacing Scale

```
xs: 4px   | sm: 8px    | md: 16px   | lg: 24px   | xl: 32px   | 2xl: 48px   | 3xl: 64px
```

### Typography

- **Display**: Bold, 36px, line-height 1.25
- **Headline**: Semibold, 24px, line-height 1.5
- **Subheading**: Semibold, 18px, line-height 1.5
- **Body**: Normal, 16px, line-height 1.5
- **Small**: Normal, 14px, line-height 1.5
- **Caption**: Normal, 12px, line-height 1.25

### Color Palette

Dark theme with slate grays and blue accents:

- **Background**: `slate-950` to `slate-900`
- **Surface**: `slate-900` to `slate-800`
- **Border**: `slate-700`
- **Text**: `white`, `slate-300`, `slate-400`, `slate-500`
- **Accent**: Blue 500-600
- **Success**: Green 500
- **Warning**: Amber 500
- **Error**: Red 500

### Animations

- **Fast**: 150ms (micro-interactions)
- **Normal**: 300ms (transitions)
- **Slow**: 500ms (page transitions)
- **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)` (standard)

## Components

### Global Components

#### CommandPalette

Global command/search interface. Triggered with Cmd/Ctrl+K.

```tsx
<CommandPalette commands={commands} />
```

#### Toast Notifications

```tsx
const toast = useToast();
toast.success("Upload complete");
toast.error("Something went wrong");
```

#### Skeleton Loading

```tsx
<Skeleton className="h-4 w-full" />
<SkeletonCard />
<SkeletonGrid count={6} />
```

#### ErrorBoundary

Graceful error handling.

```tsx
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>
```

## UX Patterns

### Loading States

Never show "Loading...". Instead, use:

1. Skeleton screens for immediate feedback
2. Step-by-step progress for long operations
3. Estimated time remaining for duration predictions

### Error Handling

1. **Friendly message**: "Upload failed. Please try again."
2. **Reason**: "File exceeds 2GB limit"
3. **Action**: Retry button or recovery guidance
4. **Recovery**: "Try a smaller file or contact support"

### Empty States

1. **Illustration/Icon**: Visual representation
2. **Title**: What's missing
3. **Description**: Why it's empty
4. **Action**: Primary action to fill it

### Form Feedback

- Real-time validation
- Clear error messages below fields
- Success states with checkmarks
- Disabled states for invalid data

## Keyboard Shortcuts

Implement these globally:

```
Cmd/Ctrl+K     – Command palette
Cmd/Ctrl+S     – Save
Cmd/Ctrl+Z     – Undo
Cmd/Ctrl+Shift+Z – Redo
Escape         – Close modal/panel
Tab            – Focus next
Shift+Tab      – Focus previous
Space          – Play/pause (video contexts)
```

## Accessibility

### WCAG 2.1 AA Compliance

✅ **Contrast**: 4.5:1 for normal text, 3:1 for large text
✅ **Keyboard**: All interactive elements keyboard accessible
✅ **Focus**: Visible focus indicators
✅ **Semantics**: Proper HTML and ARIA
✅ **Motion**: Respect prefers-reduced-motion
✅ **Screen Reader**: Descriptive labels and live regions

### Implementation

```tsx
import { usePrefersReducedMotion, announce } from "@/lib/accessibility";

// Respect motion preferences
const prefersReduced = usePrefersReducedMotion();

// Announce to screen readers
announce("Upload complete");
```

## Performance

### Guidelines

- **Page Load**: < 3 seconds
- **Interaction**: < 100ms response
- **Animation**: 60fps (16.67ms per frame)
- **Images**: Lazy load outside viewport
- **Lists**: Virtualize if > 100 items

### Optimization

```tsx
import { debounce, throttle, useVirtualization } from "@/lib/performance";

// Debounce search (300ms)
const handleSearch = debounce(search, 300);

// Throttle scroll (16ms for 60fps)
const handleScroll = throttle(scroll, 16);

// Virtualize long lists
const { visibleItems } = useVirtualization({ itemHeight: 48, items });
```

## Animations

### Presets

```tsx
import { animationPresets, useAnimation } from '@/lib/animations';

// Fade in
<motion.div {...animationPresets.fadeIn}>

// Slide from left
<motion.div {...animationPresets.slideInLeft}>

// Scale in
<motion.div {...animationPresets.scaleIn}>
```

### Best Practices

- **Duration**: 300ms for most transitions
- **Easing**: cubic-bezier(0.4, 0, 0.2, 1)
- **Stagger**: 100ms between items
- **Physics**: Use spring transitions for natural feel
- **Restraint**: Less is more—no unnecessary motion

## Component Checklist

For every component, verify:

### Visual

- ✅ Consistent spacing (using scale)
- ✅ Consistent typography
- ✅ Consistent colors
- ✅ Consistent icons
- ✅ Proper contrast ratios

### Interactions

- ✅ Hover states
- ✅ Active/pressed states
- ✅ Focus indicators
- ✅ Loading states
- ✅ Disabled states
- ✅ Error states
- ✅ Empty states

### Responsiveness

- ✅ Mobile (< 640px)
- ✅ Tablet (640px - 1024px)
- ✅ Desktop (> 1024px)
- ✅ Ultra-wide (> 1536px)

### Accessibility

- ✅ Keyboard navigation
- ✅ Focus management
- ✅ ARIA labels
- ✅ Screen reader support
- ✅ Reduced motion support

### Performance

- ✅ No unnecessary re-renders
- ✅ Memoized where needed
- ✅ Lazy-loaded resources
- ✅ No prop drilling

## Quality Standards

### No Compromises On:

1. **Accessibility** – WCAG 2.1 AA minimum
2. **Performance** – 60fps animations, < 3s load
3. **Consistency** – Design system adherence
4. **Error Handling** – User-friendly messages
5. **Loading UX** – Never just "Loading..."

### Eliminate:

- Hardcoded colors (use design system)
- Duplicate components (abstract and reuse)
- Hardcoded spacing (use scale)
- Magic numbers (document constants)
- Console errors (fix before shipping)

## Testing Checklist

Before shipping features:

- [ ] Visual regression tests
- [ ] Accessibility audit (axe DevTools)
- [ ] Performance profiling (Lighthouse)
- [ ] Responsive design (all breakpoints)
- [ ] Keyboard navigation
- [ ] Dark mode
- [ ] Empty states
- [ ] Error states
- [ ] Loading states
- [ ] Cross-browser (Chrome, Firefox, Safari, Edge)

## Resources

- **Design System**: `src/lib/design-system.ts`
- **Keyboard Shortcuts**: `src/lib/keyboard-shortcuts.ts`
- **Accessibility**: `src/lib/accessibility.ts`
- **Performance**: `src/lib/performance.ts`
- **Animations**: `src/lib/animations.ts`
- **Global Components**: `src/components/global/`

## Inspiration

Study how these products handle UX:

- **Linear**: Keyboard-first, fast interactions
- **Figma**: Smooth animations, responsive
- **Notion**: Customizable, accessible
- **Vercel**: Clear feedback, helpful errors

---

**Goal**: Make AURA feel like a product people love to use every day.
