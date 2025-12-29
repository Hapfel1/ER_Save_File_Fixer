"""
Elden Ring Save Parser - UserDataX (Character Slot)

This is the MAIN sequential parser that reads an entire character slot in order.
Based on ER-Save-Lib Rust implementation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from io import BytesIO
import struct
from typing import List, Optional

from .er_types import Gaitem, MapId
from .character import PlayerGameData, SPEffect
from .equipment import (
    EquippedItemsEquipIndex, ActiveWeaponSlotsAndArmStyle,
    EquippedItemsItemIds, EquippedItemsGaitemHandles,
    Inventory, EquippedSpells, EquippedItems, EquippedGestures,
    AcquiredProjectiles, EquippedArmamentsAndItems, EquippedPhysics,
    TrophyEquipData
)
from .world import (
    FaceData, Gestures, Regions, RideGameData, BloodStain,
    MenuSaveLoad, GaitemGameData, TutorialData, FieldArea,
    WorldArea, WorldGeomMan, RendMan, PlayerCoordinates,
    NetMan, WorldAreaWeather, WorldAreaTime, BaseVersion,
    PS5Activity, DLC, PlayerGameDataHash
)


@dataclass
class UserDataX:
    """
    Complete character slot (UserDataX structure)
    
    This class sequentially parses EVERY field in exact order from the save file.
    Size: ~2.6MB per slot (varies based on version and data)
    
    CRITICAL: Field order MUST match the Rust implementation exactly!
    Any deviation will cause misalignment and data corruption.
    """
    
    # Header (4 + 4 + 8 + 16 = 32 bytes)
    version: int = 0
    map_id: MapId = field(default_factory=MapId)
    unk0x8: bytes = field(default_factory=lambda: b'\x00' * 8)
    unk0x10: bytes = field(default_factory=lambda: b'\x00' * 16)
    
    # Gaitem map (VARIABLE LENGTH! 5118 or 5120 entries)
    gaitem_map: List[Gaitem] = field(default_factory=list)
    
    # Player data (0x1B0 = 432 bytes)
    player_game_data: PlayerGameData = field(default_factory=PlayerGameData)
    
    # SP Effects (13 entries × 16 bytes = 208 bytes, but actually reads different)
    sp_effects: List[SPEffect] = field(default_factory=list)
    
    # Equipment structures
    equipped_items_equip_index: EquippedItemsEquipIndex = field(default_factory=EquippedItemsEquipIndex)
    active_weapon_slots_and_arm_style: ActiveWeaponSlotsAndArmStyle = field(default_factory=ActiveWeaponSlotsAndArmStyle)
    equipped_items_item_id: EquippedItemsItemIds = field(default_factory=EquippedItemsItemIds)
    equipped_items_gaitem_handle: EquippedItemsGaitemHandles = field(default_factory=EquippedItemsGaitemHandles)
    
    # Inventory held (CRITICAL: 0xa80 common, 0x180 key)
    inventory_held: Inventory = field(default_factory=Inventory)
    
    # More equipment
    equipped_spells: EquippedSpells = field(default_factory=EquippedSpells)
    equipped_items: EquippedItems = field(default_factory=EquippedItems)
    equipped_gestures: EquippedGestures = field(default_factory=EquippedGestures)
    acquired_projectiles: AcquiredProjectiles = field(default_factory=AcquiredProjectiles)
    equipped_armaments_and_items: EquippedArmamentsAndItems = field(default_factory=EquippedArmamentsAndItems)
    equipped_physics: EquippedPhysics = field(default_factory=EquippedPhysics)
    
    # Face data (0x12F = 303 bytes when in_profile_summary=False)
    face_data: FaceData = field(default_factory=FaceData)
    
    # Inventory storage (CRITICAL: 0x780 common, 0x80 key)
    inventory_storage_box: Inventory = field(default_factory=Inventory)
    
    # Gestures and regions
    gestures: Gestures = field(default_factory=Gestures)
    unlocked_regions: Regions = field(default_factory=Regions)
    
    # Horse/Torrent
    horse: RideGameData = field(default_factory=RideGameData)
    
    # Control byte (1 byte)
    control_byte_maybe: int = 0
    
    # Blood stain
    blood_stain: BloodStain = field(default_factory=BloodStain)
    
    # Unknown fields (8 bytes total)
    unk_gamedataman_0x120_or_gamedataman_0x130: int = 0
    unk_gamedataman_0x88: int = 0
    
    # Menu and game data
    menu_profile_save_load: MenuSaveLoad = field(default_factory=MenuSaveLoad)
    trophy_equip_data: TrophyEquipData = field(default_factory=TrophyEquipData)
    gaitem_game_data: GaitemGameData = field(default_factory=GaitemGameData)
    tutorial_data: TutorialData = field(default_factory=TutorialData)
    
    # GameMan bytes (3 bytes)
    gameman_0x8c: int = 0
    gameman_0x8d: int = 0
    gameman_0x8e: int = 0
    
    # Death and character info
    total_deaths_count: int = 0
    character_type: int = 0
    in_online_session_flag: int = 0
    character_type_online: int = 0
    last_rested_grace: int = 0
    not_alone_flag: int = 0
    in_game_countdown_timer: int = 0
    unk_gamedataman_0x124_or_gamedataman_0x134: int = 0
    
    # Event flags (MASSIVE! 0x1BF99F = 1,833,375 bytes)
    event_flags: bytes = field(default_factory=lambda: b'\x00' * 0x1BF99F)
    event_flags_terminator: int = 0
    
    # World structures
    field_area: FieldArea = field(default_factory=FieldArea)
    world_area: WorldArea = field(default_factory=WorldArea)
    world_geom_man: WorldGeomMan = field(default_factory=WorldGeomMan)
    world_geom_man2: WorldGeomMan = field(default_factory=WorldGeomMan)
    rend_man: RendMan = field(default_factory=RendMan)
    
    # Player position
    player_coordinates: PlayerCoordinates = field(default_factory=PlayerCoordinates)
    
    # More GameMan bytes
    game_man_0x5be: int = 0
    game_man_0x5bf: int = 0
    spawn_point_entity_id: int = 0
    game_man_0xb64: int = 0
    
    # Version-specific fields
    temp_spawn_point_entity_id: Optional[int] = None  # version >= 65
    game_man_0xcb3: Optional[int] = None  # version >= 66
    
    # Network and world state
    net_man: NetMan = field(default_factory=NetMan)
    world_area_weather: WorldAreaWeather = field(default_factory=WorldAreaWeather)
    world_area_time: WorldAreaTime = field(default_factory=WorldAreaTime)
    base_version: BaseVersion = field(default_factory=BaseVersion)
    steam_id: int = 0
    ps5_activity: PS5Activity = field(default_factory=PS5Activity)
    dlc: DLC = field(default_factory=DLC)
    player_data_hash: PlayerGameDataHash = field(default_factory=PlayerGameDataHash)
    
    # Any remaining bytes
    rest: bytes = b''
    
    @classmethod
    def read(cls, f: BytesIO, is_ps: bool, slot_start_offset: int, slot_size: int) -> UserDataX:
        """
        Read complete UserDataX from stream in EXACT sequential order.
        
        This is the main parsing function - follows Rust implementation exactly.
        
        Args:
            f: BytesIO stream positioned at start of character slot
            is_ps: True if PlayStation format (no checksum)
            slot_start_offset: Starting byte offset of this slot in the file
            slot_size: Total size of this slot (0x280000 for data portion)
            
        Returns:
            UserDataX instance with all fields populated
        """
        obj = cls()
        
        # Track where we started reading this slot's data
        data_start_offset = f.tell()
        
        # Read version (4 bytes)
        obj.version = struct.unpack("<I", f.read(4))[0]
        
        # Empty slot check
        if obj.version == 0:
            # For empty slots, read remaining bytes to maintain alignment
            bytes_read_so_far = f.tell() - data_start_offset
            remaining = slot_size - bytes_read_so_far
            if remaining > 0:
                obj.rest = f.read(remaining)
            return obj
        
        # Read map_id and header (4 + 8 + 16 = 28 bytes)
        obj.map_id = MapId.read(f)
        obj.unk0x8 = f.read(8)
        obj.unk0x10 = f.read(16)
        
        # Read Gaitem map (VARIABLE LENGTH!)
        gaitem_count = 0x13FE if obj.version <= 81 else 0x1400  # 5118 or 5120
        print(f"    Reading {gaitem_count} gaitems...")
        pos_before = f.tell() - data_start_offset
        obj.gaitem_map = [Gaitem.read(f) for _ in range(gaitem_count)]
        print(f"      Gaitems: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read player game data (432 bytes)
        print(f"    Reading player data...")
        pos_before = f.tell() - data_start_offset
        obj.player_game_data = PlayerGameData.read(f)
        print(f"      PlayerGameData: {f.tell() - data_start_offset - pos_before} bytes (expected 432)")
        
        # Read SP effects (13 entries)
        print(f"    Reading SP effects...")
        pos_before = f.tell() - data_start_offset
        obj.sp_effects = [SPEffect.read(f) for _ in range(13)]
        print(f"      SPEffects: {f.tell() - data_start_offset - pos_before} bytes (expected 208)")
        
        # Read equipment structures
        print(f"    Reading equipment...")
        pos_before = f.tell() - data_start_offset
        obj.equipped_items_equip_index = EquippedItemsEquipIndex.read(f)
        obj.active_weapon_slots_and_arm_style = ActiveWeaponSlotsAndArmStyle.read(f)
        obj.equipped_items_item_id = EquippedItemsItemIds.read(f)
        obj.equipped_items_gaitem_handle = EquippedItemsGaitemHandles.read(f)
        print(f"      Equipment indexes: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read inventory held (CRITICAL CAPACITIES!)
        print(f"    Reading held inventory...")
        pos_before = f.tell() - data_start_offset
        obj.inventory_held = Inventory.read(f, 0xa80, 0x180)
        print(f"      Held inventory: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read more equipment
        pos_before = f.tell() - data_start_offset
        obj.equipped_spells = EquippedSpells.read(f)
        obj.equipped_items = EquippedItems.read(f)
        obj.equipped_gestures = EquippedGestures.read(f)
        obj.acquired_projectiles = AcquiredProjectiles.read(f)
        obj.equipped_armaments_and_items = EquippedArmamentsAndItems.read(f)
        obj.equipped_physics = EquippedPhysics.read(f)
        print(f"      More equipment: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read face data (303 bytes)
        print(f"    Reading face data...")
        pos_before = f.tell() - data_start_offset
        obj.face_data = FaceData.read(f, in_profile_summary=False)
        print(f"      FaceData: {f.tell() - data_start_offset - pos_before} bytes (expected 303)")
        
        # Read inventory storage (CRITICAL CAPACITIES!)
        print(f"    Reading storage inventory...")
        pos_before = f.tell() - data_start_offset
        obj.inventory_storage_box = Inventory.read(f, 0x780, 0x80)
        print(f"      Storage inventory: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read gestures and regions
        print(f"    Reading gestures and regions...")
        pos_before = f.tell() - data_start_offset
        
        # Debug: Show first 32 bytes before reading gestures
        debug_pos = f.tell()
        debug_bytes = f.read(32)
        f.seek(debug_pos)
        print(f"      DEBUG: Next 32 bytes: {debug_bytes.hex()}")
        print(f"      DEBUG: As ints: {[struct.unpack('<I', debug_bytes[i:i+4])[0] for i in range(0, 32, 4)]}")
        
        # Gesture count depends on version
        # Version <= 200: 64 gestures (0x40 × 4 = 256 bytes)
        # Version > 200: 128 gestures (0x80 × 4 = 512 bytes) - DLC added more
        gesture_count = 64 if obj.version <= 200 else 128
        print(f"      Using {gesture_count} gestures for version {obj.version}")
        obj.gestures = Gestures.read_with_count(f, gesture_count)
        print(f"      Gestures: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Debug: Show bytes before reading regions
        debug_pos = f.tell()
        debug_bytes = f.read(32)
        f.seek(debug_pos)
        print(f"      DEBUG before Regions: Next 32 bytes: {debug_bytes.hex()}")
        print(f"      DEBUG: First int (count): {struct.unpack('<I', debug_bytes[0:4])[0]}")
        
        pos_before = f.tell() - data_start_offset
        obj.unlocked_regions = Regions.read(f)
        print(f"      Regions: {f.tell() - data_start_offset - pos_before} bytes")
        print(f"        Region count: {obj.unlocked_regions.count}")
        print(f"      Total bytes after gestures/regions: {f.tell() - data_start_offset}")
        
        # Read horse
        print(f"    Reading Torrent data...")
        pos_before = f.tell() - data_start_offset
        obj.horse = RideGameData.read(f)
        
        # Read control byte
        obj.control_byte_maybe = struct.unpack("<B", f.read(1))[0]
        
        # Read blood stain
        obj.blood_stain = BloodStain.read(f)
        
        # Read unknown fields
        obj.unk_gamedataman_0x120_or_gamedataman_0x130 = struct.unpack("<I", f.read(4))[0]
        obj.unk_gamedataman_0x88 = struct.unpack("<I", f.read(4))[0]
        print(f"      Torrent & blood stain: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read menu and game data
        print(f"    Reading menu and game data...")
        pos_before = f.tell() - data_start_offset
        obj.menu_profile_save_load = MenuSaveLoad.read(f)
        obj.trophy_equip_data = TrophyEquipData.read(f)
        obj.gaitem_game_data = GaitemGameData.read(f)
        obj.tutorial_data = TutorialData.read(f)
        
        # Read GameMan bytes
        obj.gameman_0x8c = struct.unpack("<B", f.read(1))[0]
        obj.gameman_0x8d = struct.unpack("<B", f.read(1))[0]
        obj.gameman_0x8e = struct.unpack("<B", f.read(1))[0]
        print(f"      Menu and game data: {f.tell() - data_start_offset - pos_before} bytes")
        print(f"      Total bytes before event flags: {f.tell() - data_start_offset}")
        
        # Read death and character info
        pos_before = f.tell() - data_start_offset
        obj.total_deaths_count = struct.unpack("<I", f.read(4))[0]
        obj.character_type = struct.unpack("<i", f.read(4))[0]
        obj.in_online_session_flag = struct.unpack("<B", f.read(1))[0]
        obj.character_type_online = struct.unpack("<I", f.read(4))[0]
        obj.last_rested_grace = struct.unpack("<I", f.read(4))[0]
        obj.not_alone_flag = struct.unpack("<B", f.read(1))[0]
        obj.in_game_countdown_timer = struct.unpack("<I", f.read(4))[0]
        obj.unk_gamedataman_0x124_or_gamedataman_0x134 = struct.unpack("<I", f.read(4))[0]
        print(f"      Character info: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read event flags (MASSIVE!)
        print(f"    Reading event flags (1.8MB)...")
        pos_before = f.tell() - data_start_offset
        obj.event_flags = f.read(0x1BF99F)
        obj.event_flags_terminator = struct.unpack("<B", f.read(1))[0]
        print(f"      Event flags: {f.tell() - data_start_offset - pos_before} bytes (expected 1833376)")
        print(f"      Bytes read after event flags: {f.tell() - data_start_offset}")
        
        # Read world structures
        print(f"    Reading world structures...")
        pos_before = f.tell() - data_start_offset
        obj.field_area = FieldArea.read(f)
        print(f"      FieldArea: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.world_area = WorldArea.read(f)
        print(f"      WorldArea: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.world_geom_man = WorldGeomMan.read(f)
        print(f"      WorldGeomMan: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.world_geom_man2 = WorldGeomMan.read(f)
        print(f"      WorldGeomMan2: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.rend_man = RendMan.read(f)
        print(f"      RendMan: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read player position
        obj.player_coordinates = PlayerCoordinates.read(f)
        
        # Read more GameMan bytes
        obj.game_man_0x5be = struct.unpack("<B", f.read(1))[0]
        obj.game_man_0x5bf = struct.unpack("<B", f.read(1))[0]
        obj.spawn_point_entity_id = struct.unpack("<I", f.read(4))[0]
        obj.game_man_0xb64 = struct.unpack("<I", f.read(4))[0]
        
        # Version-specific fields
        if obj.version >= 65:
            obj.temp_spawn_point_entity_id = struct.unpack("<I", f.read(4))[0]
        if obj.version >= 66:
            obj.game_man_0xcb3 = struct.unpack("<B", f.read(1))[0]
        
        # Read network and world state
        print(f"    Reading network manager...")
        pos_before = f.tell() - data_start_offset
        obj.net_man = NetMan.read(f)
        print(f"      NetMan: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.world_area_weather = WorldAreaWeather.read(f)
        print(f"      WorldAreaWeather: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.world_area_time = WorldAreaTime.read(f)
        print(f"      WorldAreaTime: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.base_version = BaseVersion.read(f)
        print(f"      BaseVersion: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.steam_id = struct.unpack("<Q", f.read(8))[0]
        print(f"      SteamID: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.ps5_activity = PS5Activity.read(f)
        print(f"      PS5Activity: {f.tell() - data_start_offset - pos_before} bytes")
        
        pos_before = f.tell() - data_start_offset
        obj.dlc = DLC.read(f)
        print(f"      DLC: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read player data hash
        pos_before = f.tell() - data_start_offset
        obj.player_data_hash = PlayerGameDataHash.read(f)
        print(f"      PlayerGameDataHash: {f.tell() - data_start_offset - pos_before} bytes")
        
        # Read remaining bytes until slot boundary (like Rust's `rest` field)
        # Calculate: rest = (slot_start + slot_size) - current_position
        bytes_read_so_far = f.tell() - data_start_offset
        remaining_bytes = slot_size - bytes_read_so_far
        
        print(f"    Total bytes read so far: {bytes_read_so_far}")
        print(f"    Slot size: {slot_size}")
        print(f"    Remaining bytes for 'rest': {remaining_bytes}")
        
        if remaining_bytes > 0:
            obj.rest = f.read(remaining_bytes)
            print(f"    Read {len(obj.rest)} rest bytes to reach slot boundary")
        elif remaining_bytes < 0:
            print(f"    ⚠ WARNING: Read {-remaining_bytes} bytes beyond slot boundary!")
        
        print(f"    Character slot parsed successfully!")
        return obj
    
    def is_empty(self) -> bool:
        """Check if this is an empty character slot"""
        return self.version == 0
    
    def get_character_name(self) -> str:
        """Get character name with proper error handling"""
        try:
            name = self.player_game_data.character_name
            # Filter out non-printable characters
            cleaned = ''.join(c for c in name if c.isprintable() or c in ' \t\n')
            return cleaned.strip() if cleaned else "Unknown"
        except:
            return "Unknown"
    
    def get_level(self) -> int:
        """Get character level"""
        return self.player_game_data.level
    
    def has_torrent_bug(self) -> bool:
        """Check if Torrent has the infinite loading bug"""
        return self.horse.has_bug()
    
    def fix_torrent_bug(self):
        """Fix Torrent infinite loading bug"""
        self.horse.fix_bug()
    
    def has_weather_corruption(self) -> bool:
        """Check if weather data is corrupted"""
        return self.world_area_weather.is_corrupted()
    
    def has_time_corruption(self) -> bool:
        """Check if time data is corrupted (00:00:00)"""
        return self.world_area_time.is_zero()