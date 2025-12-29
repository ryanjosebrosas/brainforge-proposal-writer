# Tailwind CSS Best Practices Guide

**Use this guide when:** Writing or refactoring components with Tailwind CSS classes.

## Overall Pattern: Concentric CSS Ordering

Order utility classes from outside-in, following the box model:
```
[positioning/visibility] → [box model] → [borders] → [backgrounds] → [typography] → [visual adjustments]
```

This ordering pattern makes long class strings faster to parse and maintain.

---

## Step 1: Order Utility Classes Correctly

```tsx
// Good - Following concentric CSS order
<div className="relative z-10 flex flex-col w-full max-w-md p-4 border border-gray-200 rounded-lg bg-white text-sm font-medium shadow-lg hover:shadow-xl">

// Bad - Random ordering
<div className="bg-white text-sm border-gray-200 w-full shadow-lg p-4 flex rounded-lg relative font-medium flex-col max-w-md z-10 hover:shadow-xl border">
```

**Rules:**
- Start with positioning (`relative`, `absolute`, `z-10`)
- Then layout (`flex`, `grid`, `block`)
- Then sizing (`w-full`, `h-screen`, `max-w-md`)
- Then spacing (`p-4`, `mx-auto`)
- Then borders/backgrounds (`border`, `rounded`, `bg-white`)
- End with typography and effects (`text-sm`, `shadow-lg`)

---

## Step 2: Write Responsive Classes Properly

```tsx
// Good - Prefix ALL breakpoint-specific utilities
<div className="block lg:flex lg:flex-col lg:justify-center lg:items-start">

// Bad - Missing prefixes (unpredictable inheritance)
<div className="block lg:flex flex-col justify-center items-start">

// Good - Mobile-first pattern
<div className="text-sm sm:text-base md:text-lg">

// Good - Leveraging min-width behavior
<div className="block md:flex">  // Replaces: block sm:block md:flex lg:flex xl:flex
```

**Rules:**
- Prefix EVERY utility that applies at a breakpoint
- Remember: `sm:` = 640px+, `md:` = 768px+, `lg:` = 1024px+
- For mobile-only: Use `block sm:hidden` (not just `block`)
- Avoid redundant prefixes across all breakpoints
- Use mobile-first thinking (base = mobile, sm+ = tablet/desktop)

---

## Step 3: Minimize and Simplify Classes

```tsx
// Good - Using shorthand
<div className="mx-4 my-2">

// Bad - Redundant individual classes
<div className="ml-4 mr-4 mt-2 mb-2">

// Good - Efficient responsive spacing
<div className="p-4 lg:pt-8">

// Bad - Redundant declarations
<div className="pt-4 lg:pt-8 pr-4 pb-4 pl-4">
```

**Rules:**
- Use `mx-*`, `my-*`, `px-*`, `py-*` when values match
- Only override specific sides when needed
- Combine base + responsive overrides efficiently
- Remove duplicate declarations

---

## Step 4: Handle Margins Consistently

```tsx
// Good - Top/left margin pattern (scoped to element)
<div className="mt-4 ml-2">
<div className="mt-8 ml-2">

// Good - Bottom/right margin pattern (affects siblings)
<div className="mb-4 mr-2">
<div className="mb-8 mr-2">

// Bad - Mixing patterns
<div className="mt-4 mr-2">  // Inconsistent
<div className="mb-8 ml-2">  // Which pattern are we using?

// Good - Padding-based wrappers (avoids margin collapse)
<div className="px-4 py-6">
  <h1>Title</h1>
  <p>Content</p>
</div>
```

**Rules:**
- Pick ONE margin pattern: `mt-*/ml-*` OR `mb-*/mr-*`
- Prefer `mt-*/ml-*` for better element scoping
- Use padding for wrapper containers
- Avoid margin collapsing issues with padding

---

## Step 5: Handle Dynamic Classes Safely

```tsx
// Good - Complete class strings
<button className={isActive ? 'bg-blue-500 sm:w-1/2' : 'bg-gray-300 sm:w-full'}>

// Bad - String concatenation (breaks PurgeCSS)
<button className={`bg-blue-500 sm:w-1/${isActive ? '2' : '4'}`}>

// Good - Conditional wrapper pattern
<div className={cn(
  'flex items-center px-4',
  variant === 'primary' && 'bg-blue-500 text-white',
  variant === 'secondary' && 'bg-gray-200 text-gray-800'
)}>
```

**Rules:**
- Always use complete class names in conditionals
- Never concatenate partial class strings
- Use helper functions like `clsx` or `cn` for complex conditions
- Ensure PurgeCSS can detect all classes

---

## Step 6: Use @apply Sparingly

```tsx
// Good - Template-based component (preferred)
const Button = ({ variant }) => (
  <button className={variant === 'primary'
    ? 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600'
    : 'px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300'
  }>
);

// Only use @apply for TRUE duplication across multiple components
// In globals.css:
.btn-base {
  @apply px-4 py-2 rounded font-medium transition-colors;
}

// Then in components:
<button className="btn-base bg-blue-500 text-white">
```

**Rules:**
- Prefer component abstraction over `@apply`
- Only use `@apply` when utilities are duplicated across many components
- Don't nest `@apply` classes within other `@apply` classes
- Keep Tailwind utilities visible in templates when possible

---

## Quick Checklist

- [ ] Classes ordered: positioning → layout → sizing → spacing → borders → backgrounds → typography
- [ ] All responsive utilities have breakpoint prefixes (`lg:flex`, not orphaned `flex`)
- [ ] Used shorthand classes (`mx-4` instead of `ml-4 mr-4`)
- [ ] Picked consistent margin pattern (`mt-*/ml-*` or `mb-*/mr-*`, not mixed)
- [ ] Used padding for wrapper containers to avoid margin collapse
- [ ] Dynamic classes use complete strings (no concatenation)
- [ ] Avoided premature `@apply` - used component abstraction instead
- [ ] Tested responsive breakpoints at `sm` (640px), `md` (768px), `lg` (1024px)
