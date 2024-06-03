from src.code.game.racesim import free_simulation_interface, main_mgr
from src.code.game.menu import main_menu

# _racing_category_name = "Aper"
# _racing_class_name = "Aper 1"
# _racing_category_name = "Volo"
# _racing_class_name = "CAT-B"
# _race_track_name = "mt5t"

if __name__ == "__main__":
    # free_simulation_interface(_racing_category_name, _racing_class_name, _race_track_name, main_mgr.ready_drivers(_racing_category_name, _racing_class_name))
    while 1:
        output = main_menu()
        match output['type']:
            case "custom-race":
                free_simulation_interface(output['category'], output['class'], output['track'], output['drivers'])