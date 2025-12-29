# TypeScript Best Practices Guide

**Purpose:** Use this guide when writing or reviewing TypeScript code to ensure type safety, maintainability, and modern patterns.

## Overall Pattern

TypeScript code prioritizes **type safety** and **explicitness**. Follow these conventions:
- Enable strict mode in `tsconfig.json` to catch errors at compile time
- Explicit typing with unions for constrained values (avoid `any`)
- Modern ES6+ features: destructuring, spread, template literals, async/await
- Functional patterns: pure functions, immutability, array methods over loops

---

## Step 1: Type Safety Configuration

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitReturns": true,
    "noUnusedLocals": true,
    "forceConsistentCasingInFileNames": true
  }
}

// Use explicit types with unions
type Status = 'pending' | 'active' | 'completed';
type Role = 'admin' | 'user' | 'guest';

const userStatus: Status = 'active';

// AVOID any - use specific types
// ❌ Bad
function process(data: any) { }

// ✅ Good
function process(data: string | number) { }
```

**Rules:**
- Always enable `strict: true` in tsconfig.json
- Never use `any` type - use unions, `unknown`, or generics instead
- Use literal types for constrained string/number values
- Let TypeScript infer simple types (don't over-annotate)
- Use `interface` for object shapes, `type` for unions/intersections

---

## Step 2: Naming Conventions

```typescript
// Variables and functions - camelCase
const userName = 'John';
const isActive = true;
const hasPermission = false;

function calculateTotal(items: Item[]): number { }
function getUserById(id: string): User | null { }

// Classes and interfaces - PascalCase
class UserProfile { }
interface ApiResponse { }
type UserRole = 'admin' | 'user';

// Constants - UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const API_TIMEOUT = 5000;

// Private/protected - prefix with underscore
class Service {
  private _internalState: string;
  protected _helperMethod(): void { }
}

// Booleans - prefix with is/has/should/can
const isLoading: boolean = true;
const hasError: boolean = false;
const shouldRetry: boolean = true;
const canEdit: boolean = false;
```

**Rules:**
- Variables/functions: `camelCase`
- Classes/Interfaces/Types: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Booleans: prefix with `is`, `has`, `should`, `can`
- Use descriptive names that explain purpose without comments

---

## Step 3: Variable & Function Patterns

```typescript
// Use const/let, never var
const immutableValue = 25;
let mutableCounter = 0;

// Initialize variables when declared
const config = { timeout: 3000 };
let result = '';

// Functions: small (5-10 lines), single responsibility
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

// Parameter defaults
function greet(name = 'World'): string {
  return `Hello, ${name}`;
}

// Max 3 parameters - use objects for more
// ❌ Bad
function createUser(name: string, email: string, age: number, role: string) { }

// ✅ Good
interface CreateUserParams {
  name: string;
  email: string;
  age: number;
  role: string;
}
function createUser(params: CreateUserParams): User { }

// No flag parameters - split into separate functions
// ❌ Bad
function saveUser(user: User, sendEmail: boolean) { }

// ✅ Good
function saveUser(user: User): void { }
function saveUserAndNotify(user: User): void { }
```

**Rules:**
- Use `const` by default, `let` when reassignment needed
- Never use `var`
- Keep functions small (5-10 lines max)
- Limit to 3 parameters, use objects for more
- Avoid flag parameters - create separate functions

---

## Step 4: Modern TypeScript Features

```typescript
// Template literals
const message = `User ${name} logged in at ${timestamp}`;

// Destructuring
const { id, name, email } = user;
const [first, second, ...rest] = items;

// Spread operator
const merged = { ...defaults, ...userConfig };
const combined = [...array1, ...array2];

// Array methods over loops
const active = users.filter(u => u.isActive);
const names = users.map(u => u.name);
const total = prices.reduce((sum, price) => sum + price, 0);

// Optional chaining & nullish coalescing
const userName = user?.profile?.name ?? 'Guest';
const timeout = config?.timeout ?? 3000;

// Async/await over .then()
async function fetchUser(id: string): Promise<User> {
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
}

// Use strict equality
if (value === 'active') { }  // ✅ Good
if (value == 'active') { }   // ❌ Bad
```

**Rules:**
- Template literals for string interpolation
- Destructure objects/arrays when accessing multiple properties
- Use array methods (`.map`, `.filter`, `.reduce`) over loops
- Prefer `async/await` over promise chains
- Always use `===` not `==`

---

## Step 5: Type Utilities & Patterns

```typescript
// Built-in utility types
interface User {
  id: string;
  name: string;
  email: string;
  age: number;
}

type PartialUser = Partial<User>;          // All properties optional
type ReadonlyUser = Readonly<User>;        // All properties readonly
type UserPreview = Pick<User, 'id' | 'name'>;  // Select specific props
type UserWithoutEmail = Omit<User, 'email'>;   // Exclude specific props

// Generics for reusable types
interface ApiResponse<T> {
  data: T;
  error?: string;
  status: number;
}

function fetchData<T>(url: string): Promise<ApiResponse<T>> {
  // Implementation
}

// Type guards
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

// Enums for related constants
enum HttpStatus {
  OK = 200,
  BadRequest = 400,
  Unauthorized = 401,
  NotFound = 404
}
```

**Rules:**
- Use utility types (`Partial`, `Readonly`, `Pick`, `Omit`) to derive types
- Use generics for reusable, type-safe functions and interfaces
- Prefer `const` enums or union types over regular enums
- Create type guards for runtime type checking
- Use `unknown` instead of `any` when type is truly unknown

---

## Step 6: Error Handling & Quality

```typescript
// Always throw Error objects
throw new Error('User not found');
// ❌ Bad: throw 'error';

// Validate external data
function processFormData(data: unknown): User {
  if (!isValidUserData(data)) {
    throw new Error('Invalid user data');
  }
  return data;
}

// Use named constants for magic numbers
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT_MS = 5000;

for (let i = 0; i < MAX_RETRY_ATTEMPTS; i++) {
  // Retry logic
}

// Switch with default case
function getIcon(type: string): string {
  switch (type) {
    case 'success': return '✓';
    case 'error': return '✗';
    case 'warning': return '⚠';
    default: return '•';
  }
}

// Prefer pure functions (same input = same output, no side effects)
function add(a: number, b: number): number {
  return a + b;
}
```

**Rules:**
- Throw `Error` objects, not strings
- Validate all external data (forms, APIs, URLs)
- Use named constants instead of magic numbers
- Always include `default` case in switch statements
- Prefer pure functions for easier testing and reasoning

---

## Quick Checklist

- [ ] Enabled `strict: true` in tsconfig.json
- [ ] No `any` types (use unions, `unknown`, or generics)
- [ ] All names follow conventions (camelCase, PascalCase, UPPER_SNAKE_CASE)
- [ ] Booleans prefixed with is/has/should/can
- [ ] Used `const` by default, `let` when needed (never `var`)
- [ ] Functions small (5-10 lines) with ≤3 parameters
- [ ] Template literals for string interpolation
- [ ] Array methods (`.map`, `.filter`) over loops
- [ ] Optional chaining (`?.`) and nullish coalescing (`??`)
- [ ] `async/await` for promises (not `.then()`)
- [ ] Strict equality (`===`) not loose (`==`)
- [ ] Used utility types (`Partial`, `Pick`, `Omit`, `Readonly`)
- [ ] External data validated before processing
- [ ] Named constants for magic numbers
- [ ] Switch statements have default case
