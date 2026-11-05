# UI Component Quick Start Guide

## 🚀 Getting Started

The AURA desktop app now features a comprehensive, enterprise-grade design system with beautiful UI components.

## 📦 Component Library

All components are located in `src/components/ui/` and exported from `src/components/ui/index.ts`.

### Import Examples

```tsx
import {
  Button,
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
  Input,
  Tooltip,
  Dialog,
  DialogContent,
  DialogFooter,
  Section
} from "@/components/ui";

import { Sidebar } from "@/components/layout/sidebar";
import { Hero } from "@/components/sections/hero";
```

## 🎯 Common Patterns

### Button Groups
```tsx
import { Button } from "@/components/ui";

<div className="flex gap-3">
  <Button variant="primary">Save</Button>
  <Button variant="secondary">Cancel</Button>
</div>
```

### Status Display
```tsx
import { Badge } from "@/components/ui";

<div className="flex gap-2">
  <Badge variant="success">Active</Badge>
  <Badge variant="warning">Pending</Badge>
  <Badge variant="error">Failed</Badge>
</div>
```

### Form Section
```tsx
import { Input, Button } from "@/components/ui";

<form className="space-y-4 max-w-md">
  <Input 
    placeholder="Username"
    icon={<UserIcon />}
  />
  <Input 
    type="email"
    placeholder="Email"
    icon={<MailIcon />}
  />
  <Button variant="primary" className="w-full">
    Sign Up
  </Button>
</form>
```

### Data Card
```tsx
import { Card, CardHeader, CardTitle, CardContent, Badge } from "@/components/ui";

<Card variant="glass">
  <CardHeader>
    <div className="flex items-center justify-between">
      <CardTitle>Revenue</CardTitle>
      <Badge variant="success">+12%</Badge>
    </div>
  </CardHeader>
  <CardContent>
    <p className="text-3xl font-bold text-white">$24,500</p>
    <p className="text-sm text-slate-400">vs. last month</p>
  </CardContent>
</Card>
```

### Modal Dialog
```tsx
import { Dialog, DialogContent, DialogFooter, Button } from "@/components/ui";
import { useState } from "react";

export function MyDialog() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button onClick={() => setOpen(true)}>Open Dialog</Button>

      <Dialog
        open={open}
        onOpenChange={setOpen}
        title="Confirm Action"
        description="Are you sure you want to proceed?"
      >
        <DialogContent>
          <p>This action cannot be undone.</p>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={() => setOpen(false)}>
            Confirm
          </Button>
        </DialogFooter>
      </Dialog>
    </>
  );
}
```

### Hover Tooltip
```tsx
import { Tooltip, Button } from "@/components/ui";
import { InfoIcon } from "lucide-react";

<Tooltip 
  content="Click to learn more about this feature"
  side="right"
>
  <Button variant="ghost" size="icon">
    <InfoIcon className="h-4 w-4" />
  </Button>
</Tooltip>
```

### Section with Content
```tsx
import { Section, Card, CardHeader, CardTitle, CardContent } from "@/components/ui";
import { SettingsIcon } from "lucide-react";

<Section
  title="Preferences"
  description="Customize your experience"
  icon={<SettingsIcon className="h-4 w-4" />}
>
  <Card variant="glass">
    <CardHeader>
      <CardTitle>Theme</CardTitle>
    </CardHeader>
    <CardContent>
      <p>Dark theme is enabled</p>
    </CardContent>
  </Card>
</Section>
```

### Hero Section
```tsx
import { Hero } from "@/components/sections/hero";

<Hero
  badge="New Feature"
  subtitle="Introduction"
  title="Welcome to Studio"
  description="Professional tools for creating amazing content"
  actions={[
    { label: "Get Started", variant: "primary" },
    { label: "Learn More", variant: "secondary" }
  ]}
/>
```

## 🎨 Styling Guidelines

### Spacing
Use Tailwind spacing scale: `4px`, `8px`, `12px`, `16px`, `20px`, etc.

```tsx
<div className="space-y-4">     {/* 16px gap */}
  <div>Item 1</div>
  <div>Item 2</div>
</div>

<div className="gap-3">         {/* 12px gap */}
  {items.map(item => ...)}
</div>
```

### Responsive Breakpoints
```tsx
// Mobile-first: starts at sm: (640px), md: (768px), lg: (1024px)
<div className="px-4 md:px-6 lg:px-8">
  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
    {/* Responsive grid */}
  </div>
</div>
```

### Text Styles
```tsx
// Headings
<h1 className="font-display text-4xl font-bold">Large Title</h1>
<h2 className="font-display text-2xl font-semibold">Subtitle</h2>
<h3 className="font-display text-lg font-semibold">Card Title</h3>

// Body text
<p className="text-base text-slate-300">Regular text</p>
<p className="text-sm text-slate-400">Small text</p>
<p className="text-xs text-slate-500">Extra small text</p>
```

### Glass Effects
```tsx
// Standard glass
<div className="glass">Content</div>

// Dark glass
<div className="glass-dark">Content</div>

// With rounded corners
<div className="glass glass-md">Rounded content</div>
<div className="glass glass-lg">Large rounded</div>
```

## ✨ Animation Patterns

### Page Entry
```tsx
<div className="animate-fade-up">
  {/* Fades in and moves up on mount */}
</div>
```

### Multiple Staggered Items
```tsx
{items.map((item, idx) => (
  <div
    key={item.id}
    className="animate-fade-up"
    style={{ animationDelay: `${idx * 100}ms` }}
  >
    {item.name}
  </div>
))}
```

### Hover Effects
```tsx
// Built-in via interactive-element class
<button className="interactive-element rounded-xl bg-primary p-4">
  Lifts on hover, pressed on click
</button>
```

### Loading Animation
```tsx
<Button loading>
  Processing...
</Button>

// Shows spinner in button
```

## 📱 Responsive Patterns

### Mobile Navigation
```tsx
// Hidden on mobile, shown on md+ screens
<nav className="hidden md:flex gap-4">
  {links}
</nav>

// Shown on mobile, hidden on md+ screens
<nav className="md:hidden">
  {mobileLinkss}
</nav>
```

### Adaptive Layout
```tsx
// Single column on mobile, multi-column on desktop
<div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 lg:gap-6">
  {items}
</div>
```

### Flexible Headers
```tsx
<header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
  <div>{title}</div>
  <div className="flex gap-2">{actions}</div>
</header>
```

## 🔍 Accessibility

### Semantic HTML
```tsx
// ✅ Good
<button onClick={handleClick}>Click me</button>

// ❌ Avoid
<div onClick={handleClick} role="button">Click me</div>
```

### Focus States
```tsx
// Components have automatic focus-visible rings
<Button>Automatically accessible</Button>
```

### ARIA Labels
```tsx
<button 
  aria-label="Close dialog"
  onClick={handleClose}
>
  <X className="h-4 w-4" />
</button>
```

## 🎭 Dark Mode

All components are dark-mode by default. Light mode is not supported (as per design spec).

To ensure proper dark mode appearance:
1. Use `text-white` for headings
2. Use `text-slate-300` or `text-slate-400` for body text
3. Use `text-slate-500` for secondary/muted text
4. Use theme colors from CSS variables

## 🚀 Performance Tips

1. **Memoize Components**: Use `React.memo()` for list items
2. **Lazy Load**: Use `React.lazy()` for route components
3. **Image Optimization**: Use Next.js Image or similar
4. **Animation Performance**: GPU accelerated with `transform` and `opacity`
5. **Bundle Size**: Tree-shake unused components

## 📚 Component Showcase

View all components live in the app:
- Navigate to **Components** in the sidebar
- See all button variants, colors, animations
- Try interactive examples
- Copy component code

## 🆘 Troubleshooting

### Button not styled correctly
- Ensure you're using the `Button` component, not HTML `<button>`
- Check variant prop is valid: `primary`, `secondary`, `accent`, etc.

### Input not appearing
- Make sure `Input` is imported from `@/components/ui`
- Check parent has defined width or use `w-full`

### Dialog not animating
- Ensure `Dialog` state is properly managed with `useState`
- Check `open` and `onOpenChange` props

### Tooltip position wrong
- Adjust `side` prop: `"top"`, `"bottom"`, `"left"`, `"right"`
- Ensure parent has `relative` positioning

## 📖 Full Documentation

See `DESIGN_SYSTEM.md` for complete documentation including:
- All component APIs
- Color palette details
- Animation reference
- Customization guide
- Best practices

## 🤝 Need Help?

1. Check the component showcase page
2. Review `DESIGN_SYSTEM.md`
3. Look at component source code in `src/components/ui/`
4. Check existing page implementations for patterns
