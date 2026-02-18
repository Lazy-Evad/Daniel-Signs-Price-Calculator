# 🔍 WIREFRAME PLAN REVIEW - Nested Jobs Architecture

**Date**: 2026-02-17  
**Purpose**: Critical review of production-aligned job model before implementation  
**Status**: 🟡 AWAITING APPROVAL

---

## 📋 EXECUTIVE SUMMARY

### What This Plan Proposes

A **three-view architecture** that separates concerns:

1. **ITEMS VIEW** (Customer/Sales facing) - What we sell, how we quote
2. **BATCHES VIEW** (Production facing) - How we make, material optimization  
3. **FINANCE SUMMARY** (Management facing) - Profitability tracking

### Core Principle

> **"Items are priced individually, but produced in batches for efficiency"**

This mirrors real-world sign shop operations where:
- ✅ You quote 6× A3 decals at £34.66 each
- ✅ You produce them nested with other jobs to minimize waste
- ✅ Batch costs are allocated back to items proportionally

---

## 🎯 KEY DESIGN DECISIONS TO REVIEW

### 1. **Items vs Batches - Data Separation**

#### Current Proposal:
```
ITEM (sell entity)
  - id, description, spec, quantity
  - sell_per_item, cost_per_item, profit_per_item
  - linked_batch_id ← Points to production batch

BATCH (make entity)
  - id, batch_name, material_spec, nesting_result
  - Contains multiple items (potentially from different jobs)
  - Tracks production status (queued → printing → complete)
```

#### ✅ PROS:
- **Clean separation** - Sales sees items, Production sees batches
- **Flexible nesting** - Can combine items from multiple jobs
- **Accurate costing** - Batch costs allocated back to items based on actual usage
- **Production efficiency** - Optimize batches independently of customer quotes

#### ⚠️ CONS:
- **Complexity** - Two-layer data model vs. simple flat items list
- **Allocation logic** - Need robust algorithm to split batch costs to items
- **Timing mismatch** - Items quoted before batches are planned
- **Cost updates** - If batch costs change (material price spike), need to update items

#### 🤔 QUESTION FOR YOU:
**Do you currently batch jobs together, or does each quote become its own production run?**

- **Option A**: Each job prints separately → Simpler model, keep Items only
- **Option B**: We do batch/nest jobs → Need full Items + Batches architecture
- **Option C**: Sometimes batch, sometimes don't → Need flexible toggle

---

### 2. **Cost Allocation Strategy**

When multiple items from different jobs are in one batch, how do we split costs?

#### Proposed Algorithm:

```python
# BATCH 1 total costs
batch_material_cost = £50.00
batch_labour_cost = £20.00  # (setup: £15 + run: £5)
batch_total = £70.00

# Items in batch
Item A (Job #001): Uses 0.5 m² of 2.0 m² batch = 25%
Item B (Job #002): Uses 1.0 m² of 2.0 m² batch = 50%
Item C (Job #003): Uses 0.5 m² of 2.0 m² batch = 25%

# Allocation method: PROPORTIONAL BY AREA
Item A allocated: £70 × 0.25 = £17.50
Item B allocated: £70 × 0.50 = £35.00
Item C allocated: £70 × 0.25 = £17.50

# Result: Each item reflects TRUE cost including efficiency gains
```

#### Alternative Methods:

**Method 1: Area-Based (Proposed)**
- Pro: Fair for material-heavy jobs
- Con: Doesn't account for complexity (cutting time)

**Method 2: Time-Based**
- Pro: Accounts for labour complexity
- Con: Hard to track per-item time in batch

**Method 3: Hybrid (Area + Time)**
- Material: Split by area
- Labour setup: Split evenly
- Labour run: Split by item count or complexity

#### 🤔 QUESTION FOR YOU:
**Which feels fairest for your business? Area-based, time-based, or hybrid?**

---

### 3. **Batch Status Workflow**

#### Proposed State Machine:

```
Queued → Artwork Ready → Printing → [24h CURE] → 
Laminating → Cutting → Weeding → Packaged → 
[INSTALLATION] → Complete
```

#### Critical Points:

**CURE TIME (24h)**:
- Blocks downstream tasks (can't laminate wet print)
- Could be shorter for some inks (6-12h)
- Could be skipped for some materials (ACM panels)

🤔 **QUESTION**: Is 24h cure time standard for you, or variable by material?

**TASK DEPENDENCIES**:
- Current plan: Linear (print → cure → lam → cut)
- Alternative: Parallel (print Job A, while laminating Job B)

🤔 **QUESTION**: Do you have multiple machines allowing parallel work?

---

### 4. **Batch Creation Timing**

#### Scenario 1: Quote First, Batch Later ✅ (Proposed)

```
Monday:    Estimator creates quote, uses ESTIMATED nesting
           → Quote £200 (based on 1.5m² estimated)
Tuesday:   Customer approves
Wednesday: Production creates ACTUAL batch (1.4m² actual)
           → Item cost updated (£5 savings pass to profit)
```

**Pro**: Quote quickly, optimize later  
**Con**: Estimated vs actual cost variance

#### Scenario 2: Batch During Quote ❌ (Not Recommended)

```
Monday:    Estimator creates item, IMMEDIATELY creates batch
           → Quote £195 (based on 1.4m² actual nesting)
```

**Pro**: Exact costs upfront  
**Con**: Slow quoting, batch created before customer approves

#### 🤔 QUESTION FOR YOU:
**Do you prefer speed (estimate then optimize) or precision (optimize during quote)?**

Current plan assumes **speed**, but the nesting optimizer we built supports **precision**.

---

### 5. **Multi-Job Batching - UI Workflow**

#### Proposed Flow:

```
Production Manager View:
┌─────────────────────────────────────────────────┐
│ 📦 BATCH PLANNER                                │
├─────────────────────────────────────────────────┤
│ Available Items (Approved, Not Yet Batched):    │
│                                                 │
│ ☐ Job #041 - Item 1: 6× A3 decals (0.12m²)    │
│ ☐ Job #042 - Item 2: 10× A4 decals (0.06m²)   │
│ ☐ Job #043 - Item 1: 4× A3 decals (0.08m²)    │
│                                                 │
│ Selected Total: 0.26m² (20 items)               │
│                                                 │
│ [Run Nesting Optimizer]                         │
│                                                 │
│ Result: 155cm × 120cm = 1.86m²                  │
│ Efficiency: 85.2%                               │
│                                                 │
│ [Create Batch "Daily Small Decals - 2026-02-17"]│
└─────────────────────────────────────────────────┘
```

#### Key Features:
- ✅ Visual item picker (checkbox selection)
- ✅ Real-time nesting preview
- ✅ Batch naming (auto-suggest or manual)
- ✅ One-click batch creation

#### 🤔 QUESTION FOR YOU:
**Would you batch daily, weekly, or on-demand when queue reaches X items?**

---

### 6. **Installation Job Linking**

#### Current Proposal: Separate Entity

```
INSTALLATION JOB
  - Links to multiple ITEMS (potentially from multiple QUOTES)
  - Has own scheduling (date, time, team)
  - Tracks travel time, on-site time
  - Depends on: All linked items' batches complete
```

#### Example:

```
Install Job #15 - "ABC Motors Site Visit"
  ├─ Job #041, Item 1 (6× A3 decals)
  ├─ Job #042, Item 3 (Van graphics)
  └─ Job #044, Item 1 (Yard sign)
  
Schedule: Wednesday 09:00, Team: John + Tools
Travel: 0.5h each way
Duration: 2.5h on-site
```

#### Alternative: Installation Per Quote

```
Each QUOTE has its own INSTALLATION section
No cross-job installations
```

#### 🤔 QUESTION FOR YOU:
**Do you often combine installations for same customer/location, or always separate?**

---

## ⚠️ POTENTIAL CHALLENGES

### Challenge 1: Batch Cost Variance

**Scenario**:
- Quote estimated £200 (1.5m² material @ £133/m²)
- Actual batch used 1.8m² (less efficient nesting than estimated)
- Actual cost £240
- **Issue**: £40 loss eaten by business

**Solutions**:
1. **Price conservatively** - Quote with safety margin (e.g., +10% buffer)
2. **Update quotes** - Re-quote if batch costs differ significantly
3. **Lock batches** - Require batch plan before final quote approval
4. **Accept variance** - Track as learning data, adjust future estimates

#### 🤔 QUESTION FOR YOU:
**How much cost variance is acceptable before you'd re-quote?**

---

### Challenge 2: Orphaned Items

**Scenario**:
- Item quoted and approved
- Production creates batch
- Customer cancels AFTER batch printed
- **Issue**: Wasted material, need to allocate cost

**Solutions**:
1. **Deposits** - Require deposit before batching begins
2. **Production hold** - Don't batch until payment cleared
3. **Stock items** - Convert cancelled items to stock if generic
4. **Restocking fee** - Charge customer for work already done

#### 🤔 QUESTION FOR YOU:
**Do you have a deposit/payment-before-production policy?**

---

### Challenge 3: Rush Jobs

**Scenario**:
- Customer needs 6× A3 decals by tomorrow
- Can't wait for batch with other jobs
- **Issue**: Must print separately (higher cost, lower profit)

**Solutions**:
1. **Rush fee** - Charge premium for solo production run
2. **Priority batching** - Fast-track batch with fewer items
3. **Stock items** - Keep common sizes pre-printed

#### 🤔 QUESTION FOR YOU:
**How often do rush jobs disrupt your batching efficiency?**

---

## 🎨 UI/UX CONSIDERATIONS

### Current Calculator (v5) Capabilities

What we **already have**:
- ✅ Nesting optimizer (calculates optimal layout)
- ✅ Per-item quantity input
- ✅ Material cost calculation with wastage
- ✅ Labour hours (production + installation)
- ✅ Live quote summary

What we'd **need to add** for full wireframe:
- ❌ Batch management UI (create, assign items, track status)
- ❌ Multi-job item picker
- ❌ Production schedule view (Gantt chart or kanban)
- ❌ Installation job scheduler
- ❌ Cost allocation dashboard
- ❌ Historical batch efficiency reports

### Phased Rollout Recommendation

#### Phase 1: Enhanced Single-Job Mode (IMMEDIATE) ✅
- Add Unit Economics (per-item breakdown) ← **THIS FIRST**
- Keep current single-job workflow
- Improve nesting optimizer display
- **Effort**: 2-4 hours

#### Phase 2: Batch-Aware Quoting (SHORT TERM)
- Items can reference batches
- Batch cost allocation (simple area-based)
- Production status tracking (queued → complete)
- **Effort**: 1-2 days

#### Phase 3: Multi-Job Batching (MEDIUM TERM)
- Batch planner UI (item picker)
- Cross-job nesting
- Production workflow states
- **Effort**: 3-5 days

#### Phase 4: Full Production MIS (LONG TERM)
- Installation job scheduler
- Task-level tracking (design → print → cut → install)
- Actual vs estimated variance reporting
- Role-based dashboards (Estimator, Production, Installer)
- **Effort**: 2-3 weeks

---

## 🔍 CRITICAL QUESTIONS SUMMARY

Before proceeding, please clarify:

### Business Process Questions:

1. **Batching Frequency**:
   - Do you currently batch jobs together?
   - How often? (Daily, weekly, when queue hits X items?)
   - Or does each quote print separately?

2. **Cost Allocation Preference**:
   - Area-based (material-focused)?
   - Time-based (labour-focused)?
   - Hybrid?

3. **Quote Timing**:
   - Quote with estimates, optimize later? (FAST)
   - Optimize during quote for precision? (ACCURATE)

4. **Installation Workflow**:
   - Combine installs for same customer/location?
   - Or always separate per quote?

5. **Risk Tolerance**:
   - Acceptable cost variance before re-quoting? (5%? 10%?)
   - Deposit/payment policy before production?
   - Rush job frequency?

### Technical Questions:

6. **Equipment**:
   - Multiple printers/laminators (parallel work)?
   - Cure time standard 24h or variable?

7. **Current Pain Points**:
   - What's most broken in current process?
   - Where do you lose most profit? (waste, labour, mispricing?)

8. **Priority**:
   - What would help MOST right now?
     - A) Better per-item pricing visibility? (Unit Economics)
     - B) Better material waste tracking? (Nesting analysis)
     - C) Production workflow management? (Batch statuses)
     - D) Multi-job batching? (Full wireframe)

---

## 💡 RECOMMENDED NEXT STEPS

Based on your answers, I suggest:

### Option A: START SIMPLE (Recommended)

1. **Implement Unit Economics NOW** (2-4 hours)
   - Gives immediate per-item visibility
   - No process changes required
   - Works with current single-job workflow

2. **Gather Data** (1-2 weeks)
   - Track actual nesting efficiency
   - Monitor cost variances
   - Identify batching opportunities

3. **Phase 2+ Based on Data**
   - If batching proves valuable → Build batch planner
   - If estimates are accurate → Stay simple
   - If labour tracking needed → Add task timers

### Option B: FULL BUILD (Ambitious)

1. **Implement complete wireframe** (2-3 weeks)
   - All phases at once
   - Risk: Over-engineering if not needed
   - Benefit: Future-proof system

### Option C: HYBRID (Practical)

1. **Unit Economics** (immediate)
2. **Batch references in Items** (this week)
   - Add `batch_id` field to items
   - Simple batch cost lookup
   - No multi-job batching yet
3. **Production dashboard** (next week)
   - View batches, update statuses
   - Track efficiency
4. **Multi-job batching** (if needed based on learning)

---

## 📊 DECISION MATRIX

| Approach | Speed | Complexity | Future-Proof | Risk |
|----------|-------|------------|--------------|------|
| Option A (Simple) | ⚡️⚡️⚡️ Fast | 🟢 Low | 🟡 Medium | 🟢 Low |
| Option B (Full) | 🐌 Slow | 🔴 High | 🟢 High | 🔴 High |
| Option C (Hybrid) | ⚡️⚡️ Medium | 🟡 Medium | 🟢 High | 🟡 Medium |

---

## ✅ APPROVAL CHECKLIST

Before implementing, please confirm:

- [ ] Batching approach aligns with actual business process
- [ ] Cost allocation method agreed
- [ ] Quote timing strategy selected (estimate vs optimize)
- [ ] Installation workflow clarified
- [ ] Phase 1 scope confirmed (Unit Economics only? Or more?)
- [ ] Data model approved (Items + Batches structure OK?)
- [ ] UI wireframe matches expectations

---

## 🎯 MY RECOMMENDATION

**Start with Phase 1 (Unit Economics) immediately**, then spend 1-2 weeks using it to:
- See per-item costs in real quotes
- Manually track which items could batch together
- Identify actual pain points

**Then decide** if full batch management is needed, or if simple per-item visibility solves 80% of the problem.

**Reason**: Avoid building complex infrastructure for a problem that might not exist. Let real data drive Phase 2+.

---

**What would you like to do?**

A) Implement Unit Economics now, review wireframe later  
B) Answer critical questions so we can refine wireframe  
C) Start full wireframe implementation (ambitious!)  
D) Something else?
