from src.code.game.racesim import simulation_interface, main_mgr

# _racing_category_name = "Aper"
# _racing_class_name = "Aper 1"
_racing_category_name = "Volo"
_racing_class_name = "CAT-B"
_race_track_name = "ft1t"

if __name__ == "__main__":
    simulation_interface(_racing_category_name, _racing_class_name, _race_track_name, main_mgr.ready_drivers(_racing_category_name, _racing_class_name))