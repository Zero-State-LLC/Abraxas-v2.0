# The Optimal Choice of Hypothesis Is the Weakest, Not the Shortest

**arXiv:** [2301.12987v4](https://arxiv.org/abs/2301.12987v4) (v4, 11 Apr 2024)  
**Author:** Michael Timothy Bennett (The Australian National University)  
**Venue:** Proceedings of the 16th International Conference on Artificial General Intelligence (AGI 2023), Lecture Notes in Computer Science, vol 13921. Springer. pp. 42-51.  
**DOI:** 10.1007/978-3-031-33469-6_5

## Abstract
If A and B are sets such that A ⊂ B, generalisation may be understood as the inference from A of a hypothesis sufficient to construct B. One might infer any number of hypotheses from A, yet only some of those may generalise to B. How can one know which are likely to generalise? One strategy is to choose the shortest, equating the ability to compress information with the ability to generalise (a proxy for intelligence). We examine this in the context of a mathematical formalism of enactive cognition. We show that compression is neither necessary nor sufficient to maximise performance (measured in terms of the probability of a hypothesis generalising). We formulate a proxy unrelated to length or simplicity, called **weakness**. We show that if tasks are uniformly distributed, then there is no choice of proxy that performs at least as well as weakness maximisation in all tasks while performing strictly better in at least one. In experiments comparing maximum weakness and minimum description length in the context of binary arithmetic, the former generalised at between 1.1 and 5 times the rate of the latter. We argue this demonstrates that weakness is a far better proxy, and explains why Deepmind's Apperception Engine is able to generalise effectively.

**Keywords:** simplicity · induction · artificial general intelligence.

## Core Formalism (Enactive Cognition)
- **Environment**: Set Φ of states; declarative programs P as functions Φ → {true, false}.
- **Implementable language**: Vocabulary v ⊂ P (finite); statements l ⊆ v; Lv = statements true in some state.
- **Extension**: Zl = {b ∈ Lv : l ⊆ b} (what the statement implies). Weakness of l is |Zl| (cardinality; more implications = weaker/more general hypothesis).
- **v-task** ω = ⟨Sω, Dω, Mω⟩: situations S, correct decisions D, models M (hypotheses that entail exactly D for S).
- **Induction**: From child task α ⊏ ω (Sα ⊂ Sω, Dα ⊆ Dω), select h ∈ Mα via proxy qv to generalise to ω.
- **Generalisation**: l generalises to task if l ∈ M (entails the correct decisions).
- **Proxy**: qv : Lv → N. Higher proxy → more likely to generalise.
  - **Weakness proxy**: q(l) = |Zl|.
  - **Description length (MDL) proxy**: q(l) = 1/|l| (shorter better; common in Solomonoff, AIXI, etc.).

## Key Theorems
**Proposition 1 (Sufficiency)**: Weakness maximisation is sufficient to maximise P(generalises | child α to parent ω).

Proof sketch: P(h generalises to ω | h model of α) = 2|ZSα ∩ Zh| / 2|ZSα|. This is maximised by maximising |Zh| (weakness), since larger extension covers more possible decisions outside the known child.

**Proposition 2 (Necessity)**: Weakness (or function thereof) is necessary. If |Zh| < |Dω| then cannot generalise (Dω ⊈ Zh). Max |Zh| required.

**Remark (Universal Prior-like)**: Under uniform tasks, P(generalise to ω) ∝ |Zl| / something; empty hypothesis (max weakness) is optimal absent info. Computable for finite v.

**Proposition 3**: Minimum description length (MDL) is *neither necessary nor sufficient*.

Counterexample constructed where MDL picks specific hypothesis, weakness picks the generalising one. MDL does not reliably maximise |Z|.

**Bennett’s Razor** (proposed epistemological principle): "Explanations should be no more specific than necessary." (Weakness, not simplicity per se. A simple statement can be overly strong/specific; complex can be vacuous.)

## Experiments (Binary Arithmetic)
- Tasks: 8-bit string prediction for 4-bit binary + and × (input 4 bits + output 4 bits).
- Vocabulary: Propositional logic over 8 bits (¬, ∧, ∨).
- Setup: For |Dk| examples in child (4–14), sample child from parent, induce weakest cw vs MDL cmdl models.
- Test: Reconstruct decisions from extension Zc and compare to ground truth Dn.
- Metrics: Generalisation rate (Drecon == Dn exact), extent |Drecon ∩ Dn| / |Dn|.

**Results (Table 1 Addition, Table 2 Multiplication)**:
For addition (|Dk|=6,10,14):
- Weakness (cw) rate: ~0.11, 0.27, 0.68 (vs MDL 0.10, 0.13, 0.24)
- Extent higher for cw.
- Overall: cw generalised at 1.1×–5× rate of cmdl; extent 1.03×–1.56×.

Similar for multiplication. Weakness far superior predictor of generalisation.

## Implications for Self-Improvement Surfaces
This paper directly challenges reliance on "shortest / simplest / most compressive" hypotheses in induction, evolution, prompt engineering, skill patching, and learning systems (common in MDL, AIXI-inspired, many LLM evolution loops).

**For self-improvement / skill evolution / darwinian evolution**:
- When generating or selecting candidate patches, prompts, patterns, or "hypotheses" from traces/learnings/outcomes:
  - **Prioritize weakness** (max |extension| / generality / coverage / applicability) over length, token count, or syntactic simplicity.
  - Measure proxies for weakness: breadth of successful application (across diverse tasks/projects), coverage of edge cases without over-specificity, abstraction level (universal rules > instance-specific), failure to overfit.
  - In replay/canary/eval: Score not only accuracy/success_rate but generality (how many unseen child/parent tasks it covers).
- Explains success of systems like Apperception Engine: strong inductive bias toward *general* (universally quantified, weak) assertions rather than short ones.
- For neural/LLM contexts: Grokking and robust generalization may benefit from explicit weakness optimization (vs pure loss minimization which can lead to specific/overfit solutions).
- In practice (e.g., evolve_from_use, abx-hermes-analyzer, darwinian mutator/evaluator):
  - Add "weakness_score" or generality metric.
  - Bias selection: argmax (performance + lambda * weakness_proxy).
  - Penalize overly specific (strong) hypotheses that succeed narrowly but fail broadly.
- Uniform task assumption: In real self-improvement, if "tasks" (user queries, ops traces, failure modes) are diverse/uniform-ish, weakness dominates.

## References & Appendices
- Full paper + appendices (code for experiments): arXiv + GitHub (ViscousLemming/Technical-Appendices).
- Related Bennett work on enactive cognition, symbol emergence, AIXI critiques.
- Contrast: Solomonoff induction, Kolmogorov complexity, AIXI (compression-centric).

**Integration status**: This reference is being wired into Abraxas/Hermes self-improvement surfaces (abx-hermes-skill-evolution, hermes-skill-evolution, self-improvement, darwinian-evolver, evolve scripts, literature corpora, agent doctrines) per user directive. Prefer weakness in all hypothesis selection, candidate ranking, pattern promotion, and evolution fitness.

Last updated: $(date)
