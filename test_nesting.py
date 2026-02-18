"""
Test script for Nesting Optimizer
Demonstrates the A3 signs example from the user's request
"""

from utils.nesting_optimizer import NestingOptimizer

# Example: 6 × A3 Signs on 155cm wide material
print("="*70)
print("NESTING OPTIMIZER TEST - A3 SIGNS EXAMPLE")
print("="*70)

# Job specs
item_width_cm = 29.7  # A3 width
item_height_cm = 42.0  # A3 height
quantity = 6
material_width_cm = 155.0
bleed_mm = 3.0
gutter_mm = 5.0

print(f"\n📋 JOB SPECIFICATIONS:")
print(f"   Item Size: {item_width_cm}cm × {item_height_cm}cm (A3)")
print(f"   Quantity: {quantity}")
print(f"   Material Width: {material_width_cm}cm")
print(f"   Bleed: {bleed_mm}mm | Gutter: {gutter_mm}mm")

# Calculate nesting
result = NestingOptimizer.calculate_nesting(
    item_width_cm, item_height_cm, quantity,
    material_width_cm, None,  # None = roll media
    bleed_mm, gutter_mm
)

best = result['best_layout']
savings = result['savings']

print(f"\n✅ BEST LAYOUT: {best['orientation']}")
print(f"   Grid: {best['layout_description']}")
print(f"   Material Size: {best['material_width_cm']:.1f}cm (W) × {best['material_length_cm']:.1f}cm (L)")
print(f"   Total Area: {best['total_area_m2']:.4f} m²")
print(f"   Efficiency: {best['efficiency_percent']:.1f}%")
print(f"   Waste: {best['waste_area_cm2']:.0f} cm²")

print(f"\n💰 SAVINGS vs INDIVIDUAL PRICING:")
individual = result['individual_comparison']
print(f"   Individual Method: {individual['total_area_cm2']/10000:.4f} m² (Eff: {individual['efficiency_percent']:.1f}%)")
print(f"   Nested Method: {best['total_area_m2']:.4f} m²")
print(f"   Material Saved: {savings['material_saved_cm2']/10000:.4f} m²")
print(f"   Waste Reduction: {savings['waste_reduction_percent']:.1f}%")

print(f"\n💵 COST COMPARISON (example at £100/m²):")
cost_individual = (individual['total_area_cm2']/10000) * 100
cost_nested = best['total_area_m2'] * 100
print(f"   Individual Pricing: £{cost_individual:.2f}")
print(f"   Nested Pricing: £{cost_nested:.2f}")
print(f"   SAVINGS: £{cost_individual - cost_nested:.2f} ({((cost_individual-cost_nested)/cost_individual*100):.1f}%)")

# Show both layouts
print("\n" + "="*70)
print("LAYOUT COMPARISON")
print("="*70)

for layout in result['all_layouts']:
    print(f"\n{layout['orientation'].upper()} ORIENTATION:")
    print(f"   {layout['items_across']} across × {layout['items_down']} down")
    print(f"   Material: {layout['material_width_cm']:.1f}cm × {layout['material_length_cm']:.1f}cm")
    print(f"   Efficiency: {layout['efficiency_percent']:.1f}%")
    print(f"   Total Area: {layout['total_area_m2']:.4f} m²")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70)
