# Affordability Model — Mathematical Specification

## Principle
User-declared budgets dominate generic ratios.

## Rental
Inputs:
- ideal monthly housing budget;
- comfortable budget;
- absolute max;
- estimated utilities;
- transport delta;
- recurring housing costs.

Outputs:
- housing-only fit;
- total-cost fit;
- margin after housing.

## Purchase
Inputs:
- savings;
- desired buffer;
- available down payment;
- purchase costs;
- mortgage rate/term inputs;
- debts;
- user max monthly payment.

Calculate:
- maximum purchase price under cash constraint;
- maximum price under monthly payment;
- binding constraint;
- total monthly cost.

## Important
External rates/taxes are versioned inputs, not constants inside code.

## Confidence
Separate:
- user-input confidence;
- market-price confidence;
- financing-input freshness.

## Tests
- monotonicity;
- cash constraint;
- payment constraint;
- edge cases;
- no negative disposable margin hidden.
