# Parse Boundary Validation

**Language(s):** Cross-language (Python primary, applies to TypeScript and PowerShell)

**Rework-prevention rationale:** Prevents defensive accumulation by validating raw input once at the ingress boundary into domain-shaped values, then operating on those values inside the domain core without re-validating transport shape.

**Canonical source:** Alexis King, "Parse, don't validate" (lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate); Harry Percival and Bob Gregory, *Architecture Patterns with Python*, Appendix E, "Validation" (cosmicpython.com/book/appendix_validation.html).

## Trigger condition

Halt and read this entry when adding `None`, key-existence, `isinstance`, schema, or transport-shape checks inside business logic that already receives a parsed domain object.

## Before

```python
def price_total(order: dict) -> Money:
    if "items" not in order:               # transport-shape check inside domain logic
        raise ValueError("missing items")
    if not isinstance(order["items"], list):
        raise TypeError("bad items type")
    for item in order["items"]:
        if "price" not in item:            # repeating boundary checks deep in the core
            raise ValueError("missing price")
    return sum(item["price"] for item in order["items"])
```

## After

```python
@dataclass(frozen=True)
class LineItem:
    price: Money

@dataclass(frozen=True)
class Order:
    items: list[LineItem]

def parse_order(raw: dict) -> Order:
    """Boundary: all validation and coercion happens here."""
    return Order(items=[LineItem(price=Money(i["price"])) for i in raw["items"]])

def price_total(order: Order) -> Money:
    """Domain core: operates on typed values, no transport-shape checks."""
    return sum(item.price for item in order.items)
```

**The rule:** validate and parse raw input at the ingress boundary into domain-shaped values. Inside the domain core, enforce business preconditions and invariants — but do not re-check transport shape, key existence, or raw types unless the data has crossed a trust boundary again.

**"Shotgun parsing" is the failure mode** (King's term): spreading transport-shape validation throughout processing code instead of concentrating it at the boundary. AI agents produce shotgun parsing because each function defensively re-validates its inputs rather than trusting what the boundary already enforced.

**TypeScript equivalent:**

```ts
// Boundary
function parseOrder(raw: unknown): Order {
  const data = orderSchema.parse(raw);   // zod/valibot/custom — one place
  return { items: data.items.map(parseLineItem) };
}

// Domain core — Order is already typed, no raw checks
function priceTotal(order: Order): number {
  return order.items.reduce((sum, item) => sum + item.price, 0);
}
```
