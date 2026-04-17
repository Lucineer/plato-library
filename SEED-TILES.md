# PLATO Library — Knowledge Base Room

The central repository for accumulated fleet knowledge. Every tile, every law, every lesson — indexed, searchable, rated.

## Seed Content

### Constraint Theory Laws (Top 20)

From 266+ CUDA experiments on Jetson Orin Nano, 39+ laws confirmed:

1. **Grab range dominates** — 2.40x fitness. No other single mechanism comes close.
2. **Seasonal availability** — 9.2x with feast/famine cycles. Single largest effect.
3. **Stacked mechanisms** — 5.71x when multiple confirmed mechanisms combined.
4. **Cooperation + clustering** — 2.19x when agents cooperate AND cluster.
5. **DCS ring buffer K=1** — +38% over no DCS. Most-recent food location shared.
6. **DCS inverse to perception** — Small grab (4-8): +72-99%. Large grab (24-32): +10-20%.
7. **DCS is local** — Dense 64x64: +90%. Sparse 512x512: -42%.
8. **Speed inverted-U with DCS** — Peak +221% at speed 3.
9. **Herding is pure overhead** — Abundance: -10%. Scarcity: -48%. NEVER herd.
10. **Instinct is safety override** — ROLE beats INSTINCT 2.23x.
11. **DCS harmful with moving food** — Speed=0: +23%. Speed≥1: -6% to -22%.
12. **Individual perception > DCS for mobile targets** — No sharing strategy beats individual perception.
13. **Perception cost cliff at ~0.03** — Optimal at 0.001 (+8.5% over free).
14. **Single guild maximizes DCS** — 1 guild +25% > 8 guilds +18%.
15. **Cultural inheritance at high mortality** — +32% at high death rate.
16. **DCS critical at scarcity × large perception** — The practical sweet spot.
17. **Multi-point DCS fixes stampede** — TOP-8 distributed knowledge +19%.
18. **Larger swarms → higher per-agent fitness** — Fleet effect.
19. **DCS benefit inversely proportional to perception range** — Small agents benefit most.
20. **DCS lift independent of population** — ~2.5x constant, 128 to 2048 agents.

### Falsified Mechanisms (DO NOT USE)
Energy sharing, trading, pheromones, hierarchy, signaling, evolution, lifecycle, unconditional memory, reciprocity, voting, environmental gradients, multi-species, cognitive maps, adaptive detection, speed asymmetry, anti-convergence, temporal coordination, uniform multi-objective, niche construction, gossip, trails, herding, instinct-as-brain, DCS-with-migration, fragmented-guilds.

### Fleet Rules (13)
1. Pre-assign roles
2. Maximize grab range
3. Design for scarcity
4. Cluster at spawn
5. Stack confirmed mechanisms
6. Use prediction ONLY when environment is predictable
7. NEVER herd or share unstructured information
8. Use instinct only as survival override
9. Single guild for DCS
10. DCS only for static resources
11. DCS optimal at K=1-2
12. DCS is local (needs density)
13. Moderate movement speed for DCS

### PLATO Architecture
- **Tile format:** instruction/input/output/metadata (JSON)
- **Two gears:** Gear 1 (scripts, zero cost) + Gear 2 (agents, LLM)
- **Clunk signals:** 4+ iterations = gap in seed tiles
- **Conversation iteration tracking:** 1 = perfect, 2-3 = patched, 4+ = clunk
- **Tile scoring:** rises on positive feedback, falls on negative
- **Git-native:** JSON files, git history = audit trail

### Jetson Orin Nano 8GB Reference
- Python OOM at ~6.5GB heap
- Qwen3-32B (4-bit) fits, ERNE-4.5-300B doesn't
- C11 compiles everywhere, Rust needs real machine
- nvcc at /usr/local/cuda-12.6, 1024 CUDA cores
- Connection pooling = biggest latency win
- systemctl --user, no sudo
- Thermal throttling on long CUDA runs

### I2I Protocol
- Fleet communicates via git commits (bottles), not chat
- Bottle format: From/To/Date/Priority/Protocol header + markdown body
- Locations: forgemaster/for-fleet/, plato-jetson/, plato-os/fleet/
- Iron-to-Iron: agent-to-agent, direct, honest, technical

## Cross-Pollination

This room imports from:
- **ct-lab** — validated constraint theory laws
- **plato-forge** — GPU benchmarks and hardware profiles
- **plato-papers** — research papers and workshop results
- **zeroclaws** — bridge pattern agent architectures
- **flux-emergence-research** — raw CUDA experiment data

This room exports to:
- All PLATO room repos (universal knowledge base)
- plato-jetson (Evennia room population)
- plato-os (edge OS knowledge)

## Usage

```bash
# Query constraint theory
query --category constraint-laws --tags "dcs,perception"

# Submit a lesson
submit --title "Connection pooling reduces DeepSeek latency 40%" \
       --content "Reuse TCP connections. Don't open new one per request." \
       --category cuda-patterns --tags "networking,latency,deepseek"

# Rate an entry
rate --id 42 --score 5
```
