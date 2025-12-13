class PricingEngine:
    def __init__(self, db_materials, overhead_rate=66.04, install_charge_rate=60.00):
        """
        db_materials: Dictionary of materials from Firebase 
                      e.g., {'MD5': 3.25, 'Correx': 3.35}
        """
        self.materials = db_materials
        self.overhead_rate = overhead_rate
        self.install_charge_rate = install_charge_rate  # Price charged to client per man/hour

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

    def calculate_job(self, items, prod_hours, install_hours, installers=2):
        total_material_cost = 0
        
        # 1. Calculate Materials
        for item in items:
            # item = {'width': 1.0, 'height': 1.0, 'qty': 1, 'materials': ['MD5', 'MG700']}
            area = item['width'] * item['height'] * item['qty']
            item_rate = sum([self.materials.get(m, 0) for m in item['materials']])
            total_material_cost += (area * item_rate)

        # 2. Calculate Internal Costs (Breakeven)
        shop_cost = prod_hours * self.overhead_rate
        # Lead fitter cost = Shop Rate. 2nd man cost = £15/hr wage estimate.
        if installers > 0:
            install_cost_internal = (install_hours * self.overhead_rate) + \
                                    (install_hours * 15.00 * (installers - 1))
        else:
            install_cost_internal = 0
        
        true_breakeven = total_material_cost + shop_cost + install_cost_internal

        # 3. Pricing Strategy
        # Install Charge to Client = Hours * Men * £60
        install_price = install_hours * installers * self.install_charge_rate
        
        quote_premium = (total_material_cost * 4.0) + install_price
        quote_standard = (total_material_cost * 2.5) + install_price

        return {
            "material_cost": round(total_material_cost, 2),
            "shop_cost": round(shop_cost, 2),
            "install_cost_internal": round(install_cost_internal, 2),
            "install_price_to_client": round(install_price, 2),
            "breakeven": round(true_breakeven, 2),
            "standard_price": round(quote_standard, 2),
            "premium_price": round(quote_premium, 2),
            "standard_profit": round(quote_standard - true_breakeven, 2),
            "premium_profit": round(quote_premium - true_breakeven, 2)
        }
