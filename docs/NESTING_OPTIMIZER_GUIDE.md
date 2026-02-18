# Material Nesting Optimizer - User Guide

## 🎯 Overview
The Nesting Optimizer calculates the most efficient layout for batch print jobs, dramatically reducing material waste and costs.

## 📋 Key Features

### 1. **Batch Nesting Optimizer**
- **Enable Toggle**: Turn on "Enable Batch Nesting Optimizer" to activate
- **Automatic Layout Calculation**: System tests both Portrait and Landscape orientations
- **Efficiency Analysis**: Shows waste reduction vs. individual item pricing

### 2. **Print Ready Artwork Toggle**
- **Purpose**: Indicates artwork is already prepared for production
- **Effect**: When enabled, design hours are automatically zeroed out
- **Use Case**: Client provides print-ready files

### 3. **Repeat Job Toggle**
- **Purpose**: Marks this as a repeat job with existing artwork files
- **Effect**: Design hours automatically set to zero
- **Use Case**: Re-running a previous job where artwork already exists

### 4. **Design Hours**
- **Conditional Display**: Only shown when NEITHER "Print Ready" NOR "Repeat Job" is active
- **Auto-Zero Logic**: Design time = 0 if either toggle is active
- **Integration**: Design hours included in both internal costs and billable rates

## 🔬 Example: A3 Signs (Your Scenario)

### Job Specifications:
- **Item Size**: A3 (29.7cm × 42.0cm)
- **Quantity**: 6 units
- **Material Available**: 155cm width

### Step-by-Step:

1. **Enable Nesting**: Toggle "Enable Batch Nesting Optimizer" = ON

2. **Enter Dimensions**:
   - Width: 29.7, Unit: cm
   - Height: 42.0, Unit: cm
   - Quantity: 6

3. **Nesting Parameters**:
   - Material Width: 155 cm
   - Bleed: 3mm (standard)
   - Gutter: 5mm (spacing between items)

4. **Select Materials**: Choose your vinyl/substrate from dropdown

5. **Click "CALCULATE & ADD MATERIAL"**

### What Happens:

The system will:
- ✅ Test Portrait layout (29.7cm wide items)
- ✅ Test Landscape layout (42cm wide items)
- ✅ Calculate items that fit across the 155cm width
- ✅ Determine optimal rows needed
- ✅ Calculate total material length required
- ✅ Compare waste vs. pricing each A3 individually

### Expected Results:

**Portrait Layout (29.7cm + bleed):**
- Items across: 5 (using ~148cm of 155cm width)
- Items down: 2 rows (to get 6 total, with 4 waste spots)
- Efficiency: ~85-90%

**Landscape Layout (42cm + bleed):**
- Items across: 3 (using ~126cm of 155cm width)
- Items down: 2 rows (to get 6 total)
- Efficiency: ~80-85%

**Best Layout Selected**: System chooses highest efficiency

**Savings vs Individual Pricing**:
- Individual: 6 items × full width = MASSIVE waste
- Nested: 1 optimized sheet = minimal waste
- **Typical Savings: 40-60% material cost reduction**

## 💡 Pro Tips

### Material Constraints
- **Vinyl/Laminate Max**: 160cm width (system aware)
- **Hoarding Panels**: Pre-configured for 8'×4' and 10'×5'

### Nesting Parameters
- **Bleed**: 3mm is standard for most print work
- **Gutter**: 5mm provides safe cutting space
  - Increase to 10mm for thick materials
  - Decrease to 3mm for kiss-cut work

### When to Use Nesting
✅ **USE NESTING:**
- Multiple identical items (qty > 1)
- Standard sizes that fit multiple-up
- Roll media or large sheets
- Cost-sensitive jobs

❌ **DON'T USE NESTING:**
- Single unique items (qty = 1)
- Oversized items that only fit 1-up
- When you want to quote per-item pricing

### Print Ready & Repeat Job Logic

**Scenario 1: New Job, Customer Provides Files**
- Print Ready: ✅ ON
- Repeat Job: ❌ OFF
- Design Hours: Auto = 0
- *Result: No design time charged*

**Scenario 2: Repeat Order**
- Print Ready: ❌ OFF (doesn't matter)
- Repeat Job: ✅ ON
- Design Hours: Auto = 0
- *Result: No design time charged (files already exist)*

**Scenario 3: New Job, You Create Artwork**
- Print Ready: ❌ OFF
- Repeat Job: ❌ OFF
- Design Hours: Enter actual time (e.g., 2.5 hours)
- *Result: Design time is billed*

**Scenario 4: Both Toggles ON** (shouldn't happen but handled)
- Either toggle being ON zeros design time
- System prioritizes efficiency

## 📊 Nesting Analysis Panel

When nesting is enabled, you'll see detailed analysis:

- **Orientation**: Portrait or Landscape (best efficiency)
- **Layout Grid**: e.g., "5 across × 2 down = 10 per sheet"
- **Material Size**: Exact width × length needed
- **Efficiency %**: How much of the material is used vs. wasted
- **Waste Saved**: Comparison vs. individual item pricing
- **Total Area**: Final m² to order

## 🎨 Integration with Quote System

All nesting calculations automatically integrate:
- ✅ Material costs use optimized area
- ✅ Wastage % applied to total area
- ✅ Markup calculated on efficient material use
- ✅ Labour/installation quoted separately
- ✅ PDF quote includes nesting details

## 📈 Profit Optimization

**Old Method (Individual Pricing):**
```
6 × A3 items at full width each
= 6 × (155cm × 42cm) = 3.906 m²
Cost: £100/m² = £390.60
Waste: ~60%
```

**New Method (Batch Nesting):**
```
1 optimized layout (155cm × ~90cm) = 1.395 m²
Cost: £100/m² = £139.50
Waste: ~15%
SAVINGS: £251.10 (64% reduction!)
```

**Result**: Higher margins OR more competitive pricing!

## 🔄 System Recommendations

1. **Always check nesting for quantities > 2**
2. **Review both orientations** (system auto-selects best)
3. **Adjust gutter for material type** (thicker = more space)
4. **Use Print Ready when customer supplies files**
5. **Use Repeat Job for returning orders**
6. **Design hours only when you're creating artwork**

---

**Version**: v5.0 - Nesting Optimizer Edition  
**Last Updated**: February 2026
