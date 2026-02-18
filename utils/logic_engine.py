class PricingEngine:
    def __init__(self, db_materials, overhead_rate=66.04, workshop_rate=60.00, fitting_rate=75.0, travel_rate=75.0):
        """
        db_materials: Dictionary of materials from Firebase 
        overhead_rate: Internal cost of shop per hour (for breakeven)
        workshop_rate: Billable rate for workshop time per person
        fitting_rate: Billable rate for installation time per person
        travel_rate: Billable rate for travel time per person
        """
        self.materials = db_materials
        self.overhead_rate = overhead_rate
        self.workshop_rate = workshop_rate
        self.fitting_rate = fitting_rate
        self.travel_rate = travel_rate

    @staticmethod
    def convert_to_meters(value, unit):
        """
        Converts a value from a given unit to meters.
        Supported units: 'm', 'cm', 'mm', 'ft', 'in'
        """
        if unit == 'm':
            return value
        elif unit == 'cm':
            return value / 100.0
        elif unit == 'mm':
            return value / 1000.0
        elif unit == 'ft':
            return value * 0.3048
        elif unit == 'in':
            return value * 0.0254
        return value

    def calculate_job(self, items, prod_hours, install_hours, travel_hours=0.0, installers=2, 
                      wastage_percent=0.0, markup=1.0, print_ready=False, repeat_job=False, 
                      design_hours=0.0, use_nesting=False):
        """
        Calculate job pricing with optional nesting optimization and conditional design time.
        
        Args:
            items: List of material items
            prod_hours: Production hours
            install_hours: Installation hours
            travel_hours: Travel hours
            installers: Number of installers
            wastage_percent: Material wastage percentage
            markup: Markup multiplier
            print_ready: If True, artwork is print-ready (affects design time)
            repeat_job: If True, this is a repeat job (zeros out design time)
            design_hours: Design/artwork hours (conditional on print_ready and repeat_job)
            use_nesting: If True, use optimized nesting area from item data
        
        Returns:
            Dictionary with comprehensive pricing breakdown
        """
        total_material_cost = 0
        
        # Conditional Design Time Logic
        effective_design_hours = 0.0
        if not print_ready and not repeat_job:
            effective_design_hours = design_hours
        # If print_ready=True OR repeat_job=True, design time is zeroed
        
        # 1. Calculate Materials
        for item in items:
            # Check if item has optimized nesting data
            if use_nesting and 'nesting_area_m2' in item:
                # Use the optimized batch area instead of individual calculation
                area = item['nesting_area_m2']
            else:
                # Standard individual calculation
                area = item['width'] * item['height'] * item['qty']
            
            item_rate = sum([self.materials.get(m, 0) for m in item['materials']])
            total_material_cost += (area * item_rate)

        # Apply Wastage
        wastage_cost = total_material_cost * (wastage_percent / 100.0)
        total_mat_with_waste = total_material_cost + wastage_cost

        # 2. Calculate Internal Costs (Breakeven)
        # Include design hours in workshop/production costs
        shop_cost = (prod_hours + effective_design_hours) * self.overhead_rate
        
        if installers > 0:
            install_cost_internal = (install_hours * self.overhead_rate) + \
                                    (install_hours * 15.00 * (installers - 1))
            travel_cost_internal = (travel_hours * self.overhead_rate) + \
                                   (travel_hours * 15.00 * (installers - 1))
        else:
            install_cost_internal = 0
            travel_cost_internal = 0
        
        true_breakeven = total_mat_with_waste + shop_cost + install_cost_internal + travel_cost_internal

        # 3. Pricing Strategy (Billable Rates)
        # Include design hours in billable workshop rate
        workshop_price = (prod_hours + effective_design_hours) * self.workshop_rate
        install_price = install_hours * installers * self.fitting_rate
        travel_price = travel_hours * installers * self.travel_rate

        labor_total_price = workshop_price + install_price + travel_price
        
        # Quotes: Material (w/ waste) * Markup + Total Billable Labour
        quote_price = (total_mat_with_waste * markup) + labor_total_price

        return {
            "material_cost_raw": round(total_material_cost, 2),
            "wastage_cost": round(wastage_cost, 2),
            "material_cost_total": round(total_mat_with_waste, 2),
            "shop_cost_internal": round(shop_cost, 2),
            "install_cost_internal": round(install_cost_internal, 2),
            "travel_cost_internal": round(travel_cost_internal, 2),
            "breakeven": round(true_breakeven, 2),
            "workshop_price_billed": round(workshop_price, 2),
            "install_price_billed": round(install_price, 2),
            "travel_price_billed": round(travel_price, 2),
            "labor_total_billed": round(labor_total_price, 2),
            "quote_price": round(quote_price, 2),
            "profit": round(quote_price - true_breakeven, 2),
            # Design time tracking
            "design_hours_input": design_hours,
            "design_hours_billed": effective_design_hours,
            # Job flags for audit trail
            "print_ready": print_ready,
            "repeat_job": repeat_job,
            "nesting_enabled": use_nesting
        }
