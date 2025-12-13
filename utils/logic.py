def calculate_true_cost(material_cost, prod_hours, shop_rate, install_hours, team_cost):
    """
    Calculates the True Cost (Breakeven) of a job.
    True Cost = Material Cost + (Production Hours * Shop Rate) + (Install Hours * Team Cost)
    """
    production_cost = prod_hours * shop_rate
    installation_cost = install_hours * team_cost
    return material_cost + production_cost + installation_cost

def calculate_standard_quote(material_cost, install_charge):
    """
    Calculates the Standard Quote price.
    Standard Quote = (Material * 2.5) + Installation Charge
    """
    return (material_cost * 2.5) + install_charge

def calculate_premium_quote(material_cost, install_charge):
    """
    Calculates the Premium Quote price.
    Premium Quote = (Material * 4.0) + Installation Charge
    """
    return (material_cost * 4.0) + install_charge

def calculate_material_cost(width_m, height_m, cost_per_m2):
    """
    Calculates cost of material for a specific item.
    """
    area = width_m * height_m
    return area * cost_per_m2
