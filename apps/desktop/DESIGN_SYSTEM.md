# AURA Design System

A dark, futuristic UI design system inspired by Linear, Vercel, Raycast, Apple, and OpenAI. Built with React, TypeScript, Tailwind CSS, and glassmorphism.

## 🎨 Design Principles

- **Dark Futuristic**: Professional dark theme with cyan/indigo accents
- **Glassmorphism**: Frosted glass effects with backdrop blur
- **Smooth Animations**: Polished transitions and micro-interactions
- **Responsive**: Mobile-first, adapts to all screen sizes
- **Accessibility**: WCAG compliant with proper focus states
- **Performance**: Optimized animations using CSS transforms

## 🎭 Color Palette

### Primary Colors
- **Cyan**: `#22d3ee` (`hsl(192 100% 50%)`) - Primary brand color
- **Blue**: `#3b82f6` - Secondary brand color
- **Indigo**: `#818cf8` - Accent color

### Status Colors
- **Success**: `#86efac` (`hsl(142 76% 36%)`)
- **Warning**: `#fbbf24` (`hsl(38 92% 50%)`)
- **Error**: `#ff6b6b` (`hsl(0 84% 60%)`)

### Neutrals
- **Background**: `hsl(10 14% 4%)` - Deep space
- **Foreground**: `hsl(210 40% 98%)` - Near white
- **Slate**: Various opacity levels for depth

## 📦 Components

### Button
Versatile button component with multiple variants.

```tsx
import { Button } from "@/components/ui";

<Button variant="primary" size="md">Primary Button</Button>
<Button variant="secondary" size="lg">Secondary Button</Button>
<Button variant="accent" icon={<Icon />}>With Icon</Button>
<Button variant="outline">Outlined</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="danger">Danger</Button>
```

**Variants**: `primary`, `secondary`, `accent`, `outline`, `ghost`, `danger`
**Sizes**: `sm`, `md`, `lg`, `xl`, `icon`

### Badge
Status indicators and tags.

```tsx
import { Badge } from "@/components/ui";

<Badge variant="primary">Primary</Badge>
<Badge variant="success">Success</Badge>
<Badge variant="warning">Warning</Badge>
<Badge variant="error">Error</Badge>
<Badge size="sm">Small</Badge>
```

**Variants**: `default`, `primary`, `secondary`, `success`, `warning`, `error`, `outline`
**Sizes**: `sm`, `md`, `lg`

### Card
Glassmorphic containers for content.

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui";

<Card variant="glass">
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Optional description</CardDescription>
  </CardHeader>
  <CardContent>
    {/* content */}
  </CardContent>
</Card>
```

**Variants**: `glass`, `glass-dark`, `gradient`, `solid`, `outline`

### Input
Form inputs with icons and validation.

```tsx
import { Input } from "@/components/ui";

<Input 
  placeholder="Search..." 
  icon={<SearchIcon />}
  iconPosition="left"
/>

<Input 
  placeholder="Email" 
  type="email"
  error
  helperText="Invalid email format"
/>
```

**Props**:
- `icon`: ReactNode - Icon to display
- `iconPosition`: "left" | "right" - Icon position
- `error`: boolean - Error state
- `helperText`: string - Helper text below input

### Tooltip
Hover tooltips with positioning.

```tsx
import { Tooltip } from "@/components/ui";

<Tooltip content="Help text" side="top">
  <Button>Hover me</Button>
</Tooltip>
```

**Props**:
- `content`: string | ReactNode
- `side`: "top" | "bottom" | "left" | "right"
- `delay`: number (default: 200ms)

### Dialog
Modal dialog component.

```tsx
import { Dialog, DialogContent, DialogFooter } from "@/components/ui";
import { useState } from "react";

const [open, setOpen] = useState(false);

<Dialog 
  open={open} 
  onOpenChange={setOpen}
  title="Dialog Title"
  description="Dialog description"
  size="md"
>
  <DialogContent>
    {/* content */}
  </DialogContent>
  <DialogFooter>
    <Button>Cancel</Button>
    <Button>Confirm</Button>
  </DialogFooter>
</Dialog>
```

**Props**:
- `open`: boolean
- `onOpenChange`: (open: boolean) => void
- `title`: string
- `description`: string
- `size`: "sm" | "md" | "lg" | "xl"

### Section
Grouped content with title and description.

```tsx
import { Section } from "@/components/ui";

<Section 
  title="Section Title"
  description="Optional description"
  icon={<Icon />}
>
  {/* content */}
</Section>
```

### Sidebar
Navigation sidebar with items and footer.

```tsx
import { Sidebar } from "@/components/layout/sidebar";

<Sidebar
  logo={<Logo />}
  title="App Name"
  subtitle="Subtitle"
  navItems={[
    { key: "home", label: "Home", icon: <HomeIcon /> },
    { key: "about", label: "About", icon: <AboutIcon />, badge: "3" }
  ]}
  activeItem={activeItem}
  onItemClick={handleClick}
  footer={<Footer />}
/>
```

## ✨ Animations

### Built-in Keyframes
- `fade-up` - Fade in and move up
- `fade-in` - Simple fade in
- `blur-in` - Fade in with blur effect
- `scale-in` - Scale from small to full
- `slide-in-right` - Slide in from right
- `slide-in-left` - Slide in from left
- `float` - Subtle floating motion
- `glow` - Pulsing glow effect
- `pulse-ring` - Expanding ring animation
- `shimmer` - Shimmer/shine effect

### Usage
```tsx
<div className="animate-fade-up">Fades up on mount</div>
<div className="animate-glow">Pulsing glow</div>
<div className="animate-float">Subtle float</div>
```

## 🎯 Utility Classes

### Glassmorphism
- `.glass` - Standard glass effect
- `.glass-dark` - Darker glass effect
- `.glass-sm` - Small rounded corners (2xl)
- `.glass-md` - Medium rounded corners (3xl)
- `.glass-lg` - Large rounded corners (40px)

### Glow Effects
- `.glow-primary` - Cyan glow shadow
- `.glow-accent` - Indigo glow shadow
- `.glow-sm` - Small glow
- `.text-balance` - Balanced text wrapping

### Text Effects
- `.gradient-text` - Cyan to indigo gradient
- `.gradient-text-alt` - Indigo to pink gradient

## 🎨 Tailwind Configuration

All custom animations, colors, and shadows are configured in `tailwind.config.ts`. The design system uses CSS variables for theming.

```typescript
// Access colors
bg-primary
bg-accent
bg-success
bg-warning
bg-error
text-primary
text-muted

// Animations
animate-fade-up
animate-blur-in
animate-scale-in
// ... and more
```

## 📱 Responsive Design

Components are mobile-first and responsive:

```tsx
// Example: Different layouts per breakpoint
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4">
  {/* Single column mobile, 2 columns tablet, 4 columns desktop */}
</div>
```

## 🚀 Performance Tips

1. **Animations**: Use `transform` and `opacity` for 60fps animations
2. **Lazy Loading**: Images and components load on demand
3. **CSS Variables**: Update themes without JavaScript
4. **Backdrop Blur**: Used sparingly for performance
5. **Shadows**: Optimized using CSS shadows, not multiple elements

## 🔧 Customization

### Change Primary Color
Update CSS variables in `src/styles/globals.css`:

```css
:root {
  --primary: 192 100% 50%; /* Cyan */
  --primary-light: 186 100% 69%;
  --primary-dark: 198 89% 48%;
}
```

### Add New Animation
```css
@keyframes my-animation {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@layer utilities {
  .animate-my-animation {
    animation: my-animation 0.6s ease-out both;
  }
}
```

## 📚 Component Showcase

View all components and their variations in the **Components** page in the navigation. This includes:
- All button variants and sizes
- Badge colors and states
- Card styles
- Input states
- Dialog and modals
- Animation examples
- Color palette

## 🎓 Best Practices

1. **Use semantic HTML**: Buttons are `<button>`, links are `<a>`
2. **Accessibility**: Always include `aria-` attributes where needed
3. **Loading States**: Use the `loading` prop on buttons
4. **Error States**: Use `error` and `helperText` on inputs
5. **Icons**: Use lucide-react for consistent icons
6. **Spacing**: Use Tailwind's spacing scale (4px units)
7. **Colors**: Use theme colors, not hardcoded hex values

## 📖 Resources

- [Tailwind CSS Docs](https://tailwindcss.com)
- [Lucide Icons](https://lucide.dev)
- [React Query](https://tanstack.com/query)
- [CVA (Class Variance Authority)](https://cva.style)

## 🤝 Contributing

When adding new components:

1. Create component in `src/components/ui/`
2. Use CVA for variants and styles
3. Include TypeScript interfaces
4. Export from `src/components/ui/index.ts`
5. Add to showcase view
6. Document in this file
