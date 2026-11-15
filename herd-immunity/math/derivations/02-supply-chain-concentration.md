# D2. The supply-chain limit, as a bound rather than an expectation

**Status: complete for the stated design.** This file closes open item 1 of
[`../01-theorem1-alignment.md`](../01-theorem1-alignment.md) and ledger entry 4.7,
both of which record that `r_ij -> s` was stated in expectation and needed a
bound. Certified in
[`verify_theorem1_proof.py`](../../ml-contributions/certificates/verify_theorem1_proof.py),
block P7.

---

## 1. What has to be shown

The decomposition

```
   E_i  =  sqrt(s) * E_shared  +  sqrt(1-s) * Xi_i
```

is meant to deliver `R -> (1-s)I + s 1 1'` and therefore
`N_eff -> 1 + kappa*s*(N-1)`. Saying that the cross terms vanish *in expectation*
is not enough for a stability claim: a market is unstable or not at the realized
alignment matrix, not at its mean. What the paper needs is a statement of the form
"with probability at least `1 - delta`, the realized `N_eff` is within `...` of the
closed form", so the reader knows when the closed form may be used.

**Design assumption (D).** `E_shared` and the `Xi_i` have independent entries,
mean zero, unit variance, sub-Gaussian with a common constant, and the `Xi_i` are
independent of each other and of `E_shared`.

This is an idealization and the paper says so. Real response Jacobians are
neither Gaussian nor independent across firms beyond the shared component. What
the argument actually uses is sub-Gaussian entries and independence of the
idiosyncratic parts, which is the honest scope line.

Write `D = d^2` for the ambient dimension of `vec E_i`, `u = vec E_shared`, and
`xi_i = vec Xi_i`, so `vec E_i = sqrt(s) u + sqrt(1-s) xi_i` in `R^D`.

## 2. The pointwise limit

Expanding the inner products, for `i != j`,

```
   <vec E_i, vec E_j>  =  s ||u||^2
                          +  sqrt(s(1-s)) ( u'xi_i + u'xi_j )
                          +  (1-s) xi_i'xi_j ,

   ||vec E_i||^2       =  s ||u||^2  +  2 sqrt(s(1-s)) u'xi_i  +  (1-s) ||xi_i||^2 .
```

Divide through by `D`. Under (D), `||u||^2/D` and `||xi_i||^2/D` concentrate at 1,
while `u'xi_j/D` and `xi_i'xi_j/D` concentrate at 0, all at rate `1/sqrt(D)`. So

```
   r_ij  ->  s     (i != j) ,        R  ->  R_inf := (1-s) I + s 1 1' ,
```

and `lambda_max(R_inf) = 1 + s(N-1)` exactly, by the rank-one structure of
`1 1'`. [VERIFIED, P7, at `N` in {5, 20, 50} and `s` in {0, 0.25, 0.6, 1}]

## 3. The concentration bound

**Lemma 5 (entrywise).** Under (D) there is an absolute constant `C` such that for
any `delta in (0,1)`, with probability at least `1 - delta`,

```
   max_{i != j} | r_ij - s |   <=   C * sqrt( log(N/delta) ) / d .
```

*Proof.* Each of `||u||^2/D - 1`, `||xi_i||^2/D - 1`, `u'xi_i/D` and `xi_i'xi_j/D`
is an average of `D` independent mean-zero sub-exponential terms, so Bernstein's
inequality gives a tail `2 exp(-c D t^2)` for `t in (0,1)`. There are `O(N^2)`
such quantities across all pairs. A union bound over them, with
`t = C sqrt(log(N/delta)/D)`, controls all of them simultaneously with probability
at least `1 - delta`. The ratio defining `r_ij` is a smooth function of these
quantities with bounded derivatives in a neighbourhood of the limit point, so the
same rate carries to `r_ij - s`. Substituting `sqrt(D) = d` gives the statement. []

**The `1/d` rate, and where it comes from.** The inner products average over `d^2`
matrix entries, so the fluctuation is `1/sqrt(d^2) = 1/d`. This is the origin of
the `O(1/d)` the note quotes, now attached to a probability rather than to an
expectation. [VERIFIED, P7: measured log-log slope `-1.018` against a target of
`-1`, at `N = 8`, `s = 0.6`, `d` in {8, 16, 32, 64, 128}, 40 trials per point]

**Proposition 6 (spectral).** Under the event of Lemma 5,

```
   | lambda_max(R) - (1 + s(N-1)) |   <=   C * N * sqrt( log(N/delta) ) / d ,
```

and therefore

```
   | N_eff - (1 + kappa*s*(N-1)) |    <=   kappa * C * N * sqrt( log(N/delta) ) / d .
```

*Proof.* Write `Delta = R - R_inf`, which has zero diagonal since both matrices
have unit diagonal. Weyl's inequality gives
`|lambda_max(R) - lambda_max(R_inf)| <= ||Delta||_2`, and

```
   ||Delta||_2  <=  ||Delta||_F  <=  sqrt(N(N-1)) * max_{i != j} |Delta_ij|
                <=  N * max_{i != j} |r_ij - s| .
```

Apply Lemma 5. The `N_eff` form follows by multiplying by `kappa`. []
[VERIFIED, P7: the Weyl step checked directly at `d` in {16, 64, 256}, with the
realized `|d lambda_max|` below `||Delta||_2` in every case]

## 4. What the bound says about the paper's regime

The bound matters in *relative* terms, because `N_eff` itself grows with `N`. For
large `N` the limit is `1 + s(N-1) ~ sN`, so the relative error is

```
   relative error  ~  C * sqrt(log N) / ( s * d ) ,
```

with the `N` in the numerator cancelling against the `N` in `N_eff`. The closed
form is therefore accurate once

```
   d  >>  sqrt(log N) / s ,
```

which is a condition on dimension against *vendor concentration*, not against firm
count. It degrades as `s -> 0`, which is the correct behaviour: at low shared-model
fraction the limit matrix is close to the identity and the leading eigenvalue is
determined by fluctuations rather than by the shared component.

In the instantiation the base project calibrates, `d` is in the low hundreds of
bonds and `N` is tens of firms, so with `s` above roughly `0.2` the requirement is
met with room. The paper states the condition rather than leaving it implicit,
because a referee who knows random matrix theory will ask.

## 5. The bound is loose, and by how much

The step `||Delta||_2 <= ||Delta||_F` is crude. It is used because it is
elementary and unconditional. For a `Delta` with the Wishart-type structure that
(D) actually produces, the operator norm concentrates at `sqrt(N/D) = sqrt(N)/d`
rather than at `N/d`, which would improve the relative error to
`1/(s d sqrt(N))`, that is, *better* for larger markets rather than worse.

The paper states the elementary bound as proved and the sharp rate as the measured
one, with certificate C6 reporting the fitted exponent. Claiming the sharp rate
without proving it would violate the standing rule on status flags.
[DERIVED for the crude bound; the sharp rate is measured, not proved]

## 6. Two routes to `N_eff`, and why both are kept

The theory module exposes `n_eff_supply_chain(N, s, kappa)` as the closed form and
`n_eff(supply_chain_R(N, s), kappa)` as an eigensolve of the limit matrix. They
must agree to machine precision, and certificate C2 checks exactly that. The
redundancy is deliberate: it catches a sign or index error in either route, and it
is the check that would have caught an off-by-one in `N-1`. [VERIFIED, P7, at
`N` in {5, 20, 50} and `s` in {0, 0.25, 0.6, 1}]

## 7. Status and open items

| Result | Statement | Certificate |
|---|---|---|
| Lemma 5 | `max\|r_ij - s\| <= C sqrt(log(N/delta))/d` w.h.p. | P7, slope `-1.018` |
| Prop 6 | `\|N_eff - (1 + kappa s (N-1))\| <= kappa C N sqrt(log(N/delta))/d` | P7, Weyl step |
| Limit | `lambda_max(R_inf) = 1 + s(N-1)` exactly | P7 |
| Two routes | closed form equals eigensolve of `R_inf` | P7, C2 |

**Open.**

1. The sharp operator-norm rate `sqrt(N)/d`, which needs a matrix-Bernstein or
   random-matrix argument rather than the Frobenius step. Journal material; the
   workshop reports the measured exponent. [DEFERRED]
2. Design assumption (D) is an idealization. A version under dependence across the
   `Xi_i`, which is what shared *data* rather than shared *models* would produce,
   is not attempted. [DEFERRED]
