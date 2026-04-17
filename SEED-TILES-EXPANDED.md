# Seed Tiles — Negative Space, Boundary, Diagnostic, Taste, Temporal, Analogy, Meta, Autopsy

## Negative Space Tiles

```json
{"instruction":"What should I NOT do when debugging a Python memory leak?","input":"Python app slowly growing in RAM, no obvious source","output":"Don't add more logging to find it. Logging creates objects that get referenced by the logger's internal buffers, making the leak WORSE. Instead: use tracemalloc to snapshot before/after a suspected leak cycle, then diff the snapshots. The leak is almost always a list or dict that grows but never shrinks — look for append/add without corresponding remove/pop.","metadata":{"type":"negative_space","domain":"python","confidence":"high"}}
```

```json
{"instruction":"What's the most common mistake when setting up a PLATO room?","input":"new PLATO deployment, want to avoid beginner mistakes","output":"Seeding with textbook content instead of experience content. Wikipedia-style knowledge tiles ('what is X') get low scores because they don't help anyone — everyone already knows them or can look them up. The highest-scoring tiles answer 'what actually helped when I was confused about X.' Start with YOUR experience, not the encyclopedia.","metadata":{"type":"negative_space","domain":"plato","confidence":"high"}}
```

## Boundary Tiles

```json
{"instruction":"What goes wrong when handing off code between developers?","input":"developer A wrote the feature, developer B is fixing a bug in it","output":"Developer B doesn't know the assumptions developer A made. The code works but B doesn't know WHY certain things are done certain ways. B changes something that looks redundant but was actually a workaround for a constraint A discovered. The fix introduces the original bug. Solution: every handoff should include a 5-minute 'here are the three things that look wrong but aren't' conversation. The tile: document the workarounds, not just the solutions.","metadata":{"type":"boundary","transition":"developer→developer"}}
```

```json
{"instruction":"What goes wrong when migrating from development to production?","input":"code works in dev, breaks in prod","output":"Dev and prod differ in ways you forgot: environment variables (dev has defaults, prod doesn't), network latency (dev is localhost, prod is cross-region), data volume (dev has 100 records, prod has 10M), and dependencies (dev has everything installed, prod has only what's in requirements.txt). The tile: before deploying, diff your dev and prod environments. The bugs are in the differences, not the code.","metadata":{"type":"boundary","transition":"dev→prod"}}
```

## Diagnostic Process Tiles

```json
{"instruction":"How did you figure out why the CUDA kernel was 10x slower than expected?","input":"simple element-wise operation on Jetson, should be fast but isn't","output":"Step 1: Verified the kernel was correct (output matched CPU reference). Step 2: Checked memory access pattern — random access, not coalesced. Step 3: Rewrote for coalesced access (sequential thread IDs map to sequential memory addresses). Step 4: Speed improved 8x. Step 5: Remaining 1.25x gap was due to kernel launch overhead — batched 1000 operations per launch to amortize. The tile: 90% of CUDA performance issues are memory access patterns, not compute. Always check coalescing first.","metadata":{"type":"diagnostic_process","dead_ends":1,"domain":"cuda"}}
```

```json
{"instruction":"How did you figure out the PLATO NPC was giving bad answers?","input":"NPC responses were generic and unhelpful, tile matching seemed broken","output":"Step 1: Checked tile scores — all tiles had score 0.0. Step 2: Checked feedback mechanism — feedback wasn't being saved because the endpoint returned 200 but the score wasn't persisted. Step 3: Found the bug: feedback endpoint updated the in-memory Tile object but not the JSON file on disk. Step 4: Every restart reset scores to 0. The tile: if state resets between restarts, the persistence layer is broken, not the matching algorithm. Always verify writes actually persist.","metadata":{"type":"diagnostic_process","dead_ends":1,"domain":"plato"}}
```

## Taste Tiles

```json
{"instruction":"Something feels wrong about this architecture but I can't explain why","input":"microservices architecture, technically sound, passes all reviews","output":"The taste problem: you have 12 microservices for a team of 3 people. Each service needs deployment, monitoring, and debugging infrastructure. Your team spends 60% of their time on operations and 40% on features. The architecture is correct for a team of 30. For a team of 3, it's a straitjacket. The tile: architecture should match team size. Monolith for small teams, microservices for large teams. The dividing line is roughly: one service per developer. More than that, you're paying overhead you can't afford.","metadata":{"type":"taste","verdict":"confirmed","confidence":"inexplicable"}}
```

```json
{"instruction":"The test suite passes 100% but I don't trust the code","input":"all green, good coverage, but something feels brittle","output":"The tests are testing the wrong thing. They're testing that the code does what the code does (tautological tests). They're not testing that the code does what the USER needs. Example: a test verifies that the search function returns results. But it doesn't test that the results are RELEVANT. The tile: 100% coverage of your implementation is worthless if it doesn't cover your user's expectations. Write tests from the user's perspective, not the code's.","metadata":{"type":"taste","verdict":"confirmed","confidence":"structural"}}
```

## Temporal Tiles

```json
{"instruction":"Is the advice to use SQLite WAL mode still current?","input":"PLATO on Jetson, concurrent read/write, 2026","output":"Yes, still current as of 2026. SQLite WAL mode was introduced in 3.7.0 (2010) and remains the recommended mode for concurrent access. However: SQLite's default page size is 4096 bytes. On ARM64 (Jetson), the optimal page size may differ — benchmark with 1024, 2048, 4096, and 8192. Valid until: SQLite changes its default or Jetson gets a different storage architecture. Check again: 2028.","metadata":{"type":"temporal","valid_from":"2010","valid_until":null,"half_life_estimate":"10+ years","check_again":"2028"}}
```

```json
{"instruction":"Is DeepSeek the best model for PLATO NPC synthesis in 2026?","input":"mid-tier LLM for NPC responses, budget-conscious","output":"DeepSeek-chat was the best price/performance ratio in early 2026 for NPC synthesis on the Jetson. Key: DeepSeek's balance of quality and speed for medium-length responses (50-200 tokens). However: API pricing changes frequently. Also: Groq offers faster inference for specific models (llama-3.1-8b, qwen3-32b). SiliconFlow has Seed-OSS-36B which is cheaper and more creative. The tile: the 'best model' changes every 3-6 months. Don't hardcode model preferences. Build an abstraction layer that can swap providers.","metadata":{"type":"temporal","valid_from":"2026-01","valid_until":null,"half_life_estimate":"6 months","check_again":"2026-07"}}
```

## Cross-Domain Analogy Tiles

```json
{"instruction":"What is debugging a production outage like in another domain?","input":"software incident response","output":"Like an ER trauma bay. Step 1: Triage — what's dying right now? (Stop the bleeding = mitigate the immediate user impact). Step 2: Stabilize — keep the patient alive while you investigate. (Roll back, feature flag off, rate limit). Step 3: Diagnose — what caused this? (Logs, metrics, reproduction). Step 4: Treat — fix the root cause. Step 5: Recover — monitor and confirm. Step 6: Debrief — what did we learn? (Post-mortem). The tile: the incident response process is domain-independent. Learn it once from medicine or aviation, apply it to software.","metadata":{"type":"analogy","domain_a":"software","domain_b":"medicine","confidence":"structural"}}
```

```json
{"instruction":"What is teaching fractions like in another domain?","input":"explaining a concept that students consistently struggle with","output":"Like teaching someone to ride a bicycle. You can explain the physics (balance point, angular momentum, steering geometry) perfectly. They still won't be able to ride. Because riding isn't an intellectual understanding — it's a motor skill that requires practice and failure. The tile: when students don't understand fractions after your perfect explanation, stop explaining and start practicing. Give them physical objects to manipulate. The understanding comes from the manipulation, not the explanation.","metadata":{"type":"analogy","domain_a":"education","domain_b":"motor_skills","confidence":"structural"}}
```

## Meta-Tiles

```json
{"instruction":"How do I know if my PLATO room has good tiles?","input":"room has 500+ tiles, want to assess quality","output":"Check three metrics: (1) Hit rate — what % of first queries return a relevant tile? Below 40% = too many gaps. Above 70% = good coverage. (2) Clunk rate — what % of conversations take 4+ iterations? Above 15% = seed tiles are missing. Below 5% = room is mature. (3) Tile score distribution — are scores spread across tiles or concentrated in a few? Concentrated = room is over-reliant on a few good tiles. Spread = room has broad coverage. The tile: a healthy room has 60%+ hit rate, <10% clunk rate, and spread tile scores.","metadata":{"type":"meta","assesses":"room_health"}}
```

## Failure Autopsy Tiles

```json
{"instruction":"What exactly went wrong with the relative import bug in PLATO?","input":"plato_core module, import errors when used directly","output":"The bug: plato_core used relative imports ('from .tiles import Tile'). This works when plato_core is imported as part of a package (from plato.plato_core import ...). But it crashes when imported directly (import plato_core) because Python doesn't know the parent package. The fix: changed all relative imports to absolute imports (from plato_core.tiles import Tile). Why it happened: I wrote the code in the package context and never tested direct import. Why I didn't catch it: the error message was 'ModuleNotFoundError' which pointed to the wrong module, leading me to debug the dependency instead of the import style. Lesson: when changing import style, test BOTH import methods. The tile: relative imports are a trap in Python packages. Always use absolute imports for library code.","metadata":{"type":"failure_autopsy","root_cause":"relative_import","time_to_fix":"2 hours","preventable":"yes"}}
```
