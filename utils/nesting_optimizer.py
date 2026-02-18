"""
Material Nesting Optimizer for Wide-Format Printing
Maximizes yield from roll/sheet media to minimize waste and cost
"""

import math
from typing import Dict, List, Tuple, Optional

class NestingOptimizer:
    """
    Calculates optimal nesting layouts for print jobs to minimize material waste.
    """
    
    # Standard material constraints (in cm)
    MAX_VINYL_WIDTH = 160.0  # MD5AB and Laminate maximum
    HOARDING_PANEL_SIZES = [
        (243.84, 121.92),  # 8' x 4'
        (304.8, 152.4)     # 10' x 5'
    ]
    
    @staticmethod
    def convert_to_cm(value: float, unit: str) -> float:
        """Convert value to centimeters"""
        if unit == 'm':
            return value * 100.0
        elif unit == 'cm':
            return value
        elif unit == 'mm':
            return value / 10.0
        elif unit == 'ft':
            return value * 30.48
        elif unit == 'in':
            return value * 2.54
        return value
    
    @staticmethod
    def calculate_nesting(
        item_width_cm: float,
        item_height_cm: float,
        quantity: int,
        material_width_cm: float,
        material_length_cm: Optional[float] = None,
        bleed_mm: float = 3.0,
        gutter_mm: float = 5.0
    ) -> Dict:
        """
        Calculate optimal nesting layout for Rectangle items.
        
        Args:
            item_width_cm: Width of single item in cm
            item_height_cm: Height of single item in cm
            quantity: Number of items to nest
            material_width_cm: Available material width in cm
            material_length_cm: Available material length in cm (None for roll media)
            bleed_mm: Bleed allowance in mm (added to each side)
            gutter_mm: Gutter spacing between items in mm
            
        Returns:
            Dictionary containing nesting analysis and recommendations
        """
        
        # Add bleed to item dimensions
        bleed_cm = bleed_mm / 10.0
        gutter_cm = gutter_mm / 10.0
        
        item_w_bleed = item_width_cm + (2 * bleed_cm)
        item_h_bleed = item_height_cm + (2 * bleed_cm)
        
        # Test both orientations
        layouts = []
        
        # PORTRAIT orientation (item as-is)
        portrait = NestingOptimizer._calculate_layout(
            item_w_bleed, item_h_bleed, quantity, 
            material_width_cm, material_length_cm, gutter_cm, "Portrait"
        )
        layouts.append(portrait)
        
        # LANDSCAPE orientation (item rotated 90°)
        landscape = NestingOptimizer._calculate_layout(
            item_h_bleed, item_w_bleed, quantity,
            material_width_cm, material_length_cm, gutter_cm, "Landscape"
        )
        layouts.append(landscape)
        
        # Find best layout (minimum waste)
        best_layout = min(layouts, key=lambda x: x['waste_area_cm2'])
        
        # Calculate waste comparison vs individual pricing
        individual_waste = NestingOptimizer._calculate_individual_waste(
            item_w_bleed, item_h_bleed, quantity, material_width_cm
        )
        
        return {
            'best_layout': best_layout,
            'all_layouts': layouts,
            'individual_comparison': individual_waste,
            'savings': {
                'material_saved_cm2': individual_waste['total_area_cm2'] - best_layout['total_area_cm2'],
                'waste_reduction_percent': (
                    (individual_waste['waste_area_cm2'] - best_layout['waste_area_cm2']) / 
                    individual_waste['waste_area_cm2'] * 100
                ) if individual_waste['waste_area_cm2'] > 0 else 0,
                'cost_multiplier_saved': individual_waste['cost_multiplier'] - 1.0
            },
            'item_dimensions': {
                'width_cm': item_width_cm,
                'height_cm': item_height_cm,
                'width_with_bleed_cm': item_w_bleed,
                'height_with_bleed_cm': item_h_bleed
            }
        }
    
    @staticmethod
    def _calculate_layout(
        item_width: float,
        item_height: float,
        quantity: int,
        sheet_width: float,
        sheet_length: Optional[float],
        gutter: float,
        orientation: str
    ) -> Dict:
        """Calculate layout for a specific orientation"""
        
        # Items across width (considering gutter)
        items_across = int(sheet_width / (item_width + gutter))
        if items_across < 1:
            items_across = 1
        
        # Items down length
        if sheet_length:
            items_down = int(sheet_length / (item_height + gutter))
            if items_down < 1:
                items_down = 1
            items_per_sheet = items_across * items_down
            sheets_needed = math.ceil(quantity / items_per_sheet)
            total_length = sheets_needed * sheet_length
        else:
            # Roll media - calculate length needed
            items_down = math.ceil(quantity / items_across)
            total_length = (items_down * item_height) + ((items_down - 1) * gutter) + gutter  # Add gutter margin
            sheets_needed = 1  # Continuous roll
            items_per_sheet = items_across * items_down
        
        # Calculate areas
        total_area = sheet_width * total_length
        used_area = quantity * (item_width * item_height)
        waste_area = total_area - used_area
        efficiency = (used_area / total_area * 100) if total_area > 0 else 0
        
        return {
            'orientation': orientation,
            'items_across': items_across,
            'items_down': items_down,
            'items_per_sheet': items_per_sheet,
            'sheets_needed': sheets_needed,
            'material_width_cm': sheet_width,
            'material_length_cm': total_length,
            'total_area_cm2': total_area,
            'used_area_cm2': used_area,
            'waste_area_cm2': waste_area,
            'efficiency_percent': efficiency,
            'total_area_m2': total_area / 10000.0,
            'layout_description': f"{items_across} across × {items_down} down = {items_per_sheet} per sheet"
        }
    
    @staticmethod
    def _calculate_individual_waste(
        item_width: float,
        item_height: float,
        quantity: int,
        sheet_width: float
    ) -> Dict:
        """
        Calculate waste if pricing each item individually at full sheet width.
        This is the 'worst case' approach.
        """
        # Each item would be priced at full width × item height
        area_per_item = sheet_width * item_height
        total_area = area_per_item * quantity
        used_area = quantity * (item_width * item_height)
        waste_area = total_area - used_area
        
        return {
            'total_area_cm2': total_area,
            'used_area_cm2': used_area,
            'waste_area_cm2': waste_area,
            'efficiency_percent': (used_area / total_area * 100) if total_area > 0 else 0,
            'cost_multiplier': quantity,  # Each item billed separately
            'description': f"{quantity} items × full width charging"
        }
    
    @staticmethod
    def generate_layout_visual(layout: Dict, terminal_width: int = 60) -> str:
        """
        Generate ASCII visual representation of the nesting layout
        """
        items_across = layout['items_across']
        items_down = layout['items_down']
        
        visual = []
        visual.append(f"\n{'='*terminal_width}")
        visual.append(f"LAYOUT: {layout['orientation'].upper()}")
        visual.append(f"{'='*terminal_width}")
        visual.append(f"Material: {layout['material_width_cm']:.1f}cm (W) × {layout['material_length_cm']:.1f}cm (L)")
        visual.append(f"Grid: {items_across} across × {items_down} down")
        visual.append(f"Efficiency: {layout['efficiency_percent']:.1f}%")
        visual.append("")
        
        # Simple grid representation
        cell_width = min(8, terminal_width // (items_across + 2))
        
        for row in range(items_down):
            line = "│"
            for col in range(items_across):
                line += f"{'█' * (cell_width-1)}│"
            visual.append(line)
        
        visual.append(f"{'='*terminal_width}")
        visual.append(f"Total Area Used: {layout['total_area_m2']:.4f} m²")
        visual.append(f"Waste: {layout['waste_area_cm2']:.0f} cm² ({100-layout['efficiency_percent']:.1f}%)")
        visual.append("")
        
        return "\n".join(visual)
