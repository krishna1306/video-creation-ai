# Lean Reveal.js Skill Redesign

## Problem

The current skill prioritizes framework coverage and objective compliance over presentation quality. Its generic scaffold and broad guardrails can produce technically correct but visually weak decks.

## Direction

Use a lean orchestrator with concrete composition exemplars. Keep advanced Reveal.js guidance accurate but load it only when the request needs it. Treat the generic generator as a fallback rather than the default workflow.

## Main workflow

Prioritize work in this order:

1. story and audience outcome
2. visual evidence
3. content-specific composition
4. visual identity
5. purposeful motion
6. Reveal.js mechanics
7. browser validation

Existing decks retain their visual language unless redesign is requested. New decks use concrete composition recipes derived from the MyAgent reference without automatically copying Cisco branding.

## References

- Make the design reference concrete: hero promise, evidence and explanation, outcomes, system flow, exercise split, timeline, before and after, and CTA path.
- Keep animation and Lucide references focused and optional.
- Route React, embedding, runtime APIs, scroll view, lightbox, plugins, and PDF guidance only when explicitly relevant.
- Keep the neutral scaffold and base CSS as fallback resources.

## Evaluation

Evaluate narrative clarity, composition variety, visual evidence, hierarchy, and screenshot quality. Retain objective checks for valid Reveal structure, dependency pinning, overflow, console errors, and accessibility basics.

## Success criteria

A normal presentation request should lead to a distinctive, content-led deck without requiring the model to reason through the full Reveal.js feature set. Advanced requests should still reach accurate version-specific guidance.
