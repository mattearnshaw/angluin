--import coalgebra
--import linear_algebra.matrix
--import langaut
import data.fintype

set_option eqn_compiler.max_steps 8192

@[derive decidable_eq]
inductive γ | X | Y

variables {α : Type} [decidable_eq α]

@[derive decidable_eq]
inductive finword (α : Type) : Π n : ℕ, Type
| empty {} {n : ℕ} : finword (n+1)
| nonempty {n : ℕ} : finword n → α → finword (n+1)

infixl ` ∙ ` :100 := finword.nonempty
notation `ε` := finword.empty

@[derive decidable_eq]
inductive Γ | X | Y

def maxL := 50

def t_entry (α : Type) (maxL : ℕ) := finword α maxL → finword α maxL → option bool

structure table := 
  (states : t_entry α maxL)
  (total  : t_entry α maxL.succ)

def consistent (T : table) := ∀ p₁ p₂ : finword α maxL, ∀ a : α, T.states p₁ = T.states p₂ → T.total (p₁∙a) = T.total (p₂∙a)

#print consistent

-- Rivest T2 (closed and consistent)
def t2_states: t_entry Γ maxL
| ε               ε       := tt
| (ε∙Γ.X)         ε       := ff
| _               _       := none

def t2_total : t_entry Γ (maxL+1)
--rows repeated from top, should really define total as an "extension" of top
| ε           ε := tt
| (ε∙Γ.X)     ε := ff  
| (ε∙Γ.Y)     ε := ff
| (ε∙Γ.X∙Γ.X) ε := tt
| (ε∙Γ.Y∙Γ.X) ε := ff
| _     _       := none

def table2 : table := ⟨t2_states, t2_total⟩

instance H : decidable (consistent table2) :=
begin
  unfold consistent,
  refine is_true _,
  intros,
  cases a,
  cases p₁,
  cases p₂,
  refl,
  cases p₂_a,
  cases p₂_a_1,
  have := (rfl : ε = ε),
  have b := congr a_1 this,
  have x := h,
  contradiction,
  cases p₂_a_1_a,
  cases p₂_a_1_a_1,
  --have := (of_to_bool_ff rfl) : not (table2.states ε ε = table2.states (Γ.X ∙ ε) ε) 
end

/-
@[derive decidable_eq]
inductive fin : ℕ → Type
| z {n : ℕ} : fin (n+1)
| suc {n : ℕ} : fin n → fin (n+1)

@[derive decidable_eq]
inductive fixed_word (α : Type) : ℕ → Type
| empty {} : fixed_word 0
| nonempty {n : ℕ} : α → fixed_word n → fixed_word (n+1)

inductive bounded : Π(min max : ℕ), Type
| mk (min : ℕ) {max : ℕ} : fin max → bounded min max

@[derive decidable_eq]
inductive finword (α : Type) : Π n : ℕ, fin n → Type
| empty          {n : ℕ}     : finword (n+1) fin.z
| nonempty {n : ℕ} {c : fin n} : α → finword n c → finword (n+1) c.suc

@[derive decidable_eq]
inductive range_word {α : Type} : Π(min max : ℕ), bounded min max → Type
| nonempty {min max : ℕ} {n : fin max} : fixed_word α min → finword α max n → range_word min max (bounded.mk min n)
-/
