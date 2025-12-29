"""
Test script for the complete sequential parser
"""

import sys
from pathlib import Path

# Add er_parser directory to path
sys.path.insert(0, str(Path(__file__).parent))

from er_parser import load_save


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_parser.py <save_file_path>")
        print("\nExample:")
        print("  python test_parser.py ER0000.sl2")
        print("  python test_parser.py saves/ER0000.co2")
        sys.exit(1)
    
    save_path = sys.argv[1]
    
    print("=" * 70)
    print("ELDEN RING SAVE PARSER - COMPLETE SEQUENTIAL VERSION")
    print("=" * 70)
    
    try:
        # Load and parse save file
        save = load_save(save_path)
        
        # Print summary
        save.print_summary()
        
        # Show detailed info for first active character
        active_slots = save.get_active_slots()
        if active_slots:
            slot_index = active_slots[0]
            char = save.get_slot(slot_index)
            
            print("\n" + "=" * 70)
            print(f"DETAILED INFO - Slot {slot_index}")
            print("=" * 70)
            print(f"Character Name: {char.player_game_data.character_name}")
            print(f"Level: {char.player_game_data.level}")
            print(f"\nAttributes:")
            print(f"  Vigor:        {char.player_game_data.vigor}")
            print(f"  Mind:         {char.player_game_data.mind}")
            print(f"  Endurance:    {char.player_game_data.endurance}")
            print(f"  Strength:     {char.player_game_data.strength}")
            print(f"  Dexterity:    {char.player_game_data.dexterity}")
            print(f"  Intelligence: {char.player_game_data.intelligence}")
            print(f"  Faith:        {char.player_game_data.faith}")
            print(f"  Arcane:       {char.player_game_data.arcane}")
            
            print(f"\nStats:")
            print(f"  HP: {char.player_game_data.hp}/{char.player_game_data.max_hp} (base: {char.player_game_data.base_max_hp})")
            print(f"  FP: {char.player_game_data.fp}/{char.player_game_data.max_fp} (base: {char.player_game_data.base_max_fp})")
            print(f"  SP: {char.player_game_data.sp}/{char.player_game_data.max_sp} (base: {char.player_game_data.base_max_sp})")
            
            print(f"\nResources:")
            print(f"  Runes: {char.player_game_data.runes:,}")
            print(f"  Runes Memory: {char.player_game_data.runes_memory:,}")
            print(f"  Crimson Flasks: {char.player_game_data.max_crimson_flask_count}")
            print(f"  Cerulean Flasks: {char.player_game_data.max_cerulean_flask_count}")
            
            print(f"\nGame Progress:")
            print(f"  Total Deaths: {char.total_deaths_count}")
            print(f"  Map: {char.map_id.to_decimal()}")
            print(f"  Time: {char.world_area_time}")
            print(f"  Game Version: {char.base_version.base_version}")
            print(f"  Steam ID: {char.steam_id}")
            
            print(f"\nTorrent:")
            print(f"  HP: {char.horse.hp}")
            print(f"  State: {char.horse.state.name}")
            if char.has_torrent_bug():
                print(f"  ⚠ BUG DETECTED: Infinite loading bug present!")
            
            print(f"\nInventory:")
            print(f"  Held Items: {char.inventory_held.common_item_count} common, {char.inventory_held.key_item_count} key")
            print(f"  Storage Items: {char.inventory_storage_box.common_item_count} common, {char.inventory_storage_box.key_item_count} key")
            
            print(f"\nCorruption Check:")
            issues = []
            if char.has_torrent_bug():
                issues.append("✗ Torrent infinite loading bug")
            else:
                issues.append("✓ Torrent OK")
            
            if char.has_weather_corruption():
                issues.append("✗ Weather corrupted (AreaId = 0)")
            else:
                issues.append("✓ Weather OK")
            
            if char.has_time_corruption():
                issues.append("✗ Time corrupted (00:00:00)")
            else:
                issues.append("✓ Time OK")
            
            for issue in issues:
                print(f"  {issue}")
        
        print("\n" + "=" * 70)
        print("✅ PARSING COMPLETE!")
        print("=" * 70)
        
        return 0
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())