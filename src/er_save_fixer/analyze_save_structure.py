"""
Elden Ring Save Structure Analyzer

Compares successful vs failed character slots to identify structural differences
between different save file versions.
"""

import struct
import sys
from pathlib import Path


def read_slot_data(filepath, slot_index):
    """Read raw data for a specific character slot"""
    HEADER_SIZE = 0x300
    CHECKSUM_SIZE = 0x10
    SLOT_SIZE = 0x280000
    
    with open(filepath, 'rb') as f:
        # Skip to the slot
        slot_offset = HEADER_SIZE + slot_index * (CHECKSUM_SIZE + SLOT_SIZE)
        f.seek(slot_offset)
        
        # Read checksum
        checksum = f.read(CHECKSUM_SIZE)
        
        # Read slot data
        data = f.read(SLOT_SIZE)
        
        return checksum, data


def parse_slot_header(data):
    """Parse the header of a slot to get version and basic info"""
    version = struct.unpack('<I', data[0:4])[0]
    map_id = data[4:8]
    unk0x8 = data[8:16]
    unk0x10 = data[16:32]
    
    return {
        'version': version,
        'map_id': map_id.hex(),
        'header_size': 32
    }


def find_gestures_offset(data, start_offset=0):
    """
    Try to find where gestures start by looking for repeating patterns.
    Gestures are typically u32 IDs in sequence.
    """
    # After storage inventory, we should see gestures
    # Gestures are 64 or 128 u32 values
    
    # Look for sequences of reasonable gesture IDs (typically 0-7 million range)
    candidates = []
    
    for offset in range(start_offset, min(start_offset + 50000, len(data) - 512), 4):
        # Read 8 u32s
        values = [struct.unpack('<I', data[offset + i*4:offset + i*4 + 4])[0] 
                  for i in range(8)]
        
        # Check if they look like gesture IDs (reasonable range, some patterns)
        if all(0 <= v <= 10000000 for v in values):
            # Count how many are in typical gesture ID range
            gesture_like = sum(1 for v in values if 1000000 <= v <= 7000000)
            if gesture_like >= 4:  # At least half look like gesture IDs
                candidates.append((offset, values, gesture_like))
    
    return candidates


def analyze_structure_at_offset(data, offset, num_bytes=1024):
    """Analyze structure at a specific offset"""
    chunk = data[offset:offset + num_bytes]
    
    analysis = {
        'offset': f'0x{offset:08x}',
        'hex': chunk.hex()[:200],  # First 100 bytes as hex
        'as_u32s': [],
        'patterns': []
    }
    
    # Read as u32 values
    for i in range(0, min(64, len(chunk) - 3), 4):
        val = struct.unpack('<I', chunk[i:i+4])[0]
        analysis['as_u32s'].append(val)
    
    # Look for patterns
    # All zeros?
    if chunk[:64] == bytes(64):
        analysis['patterns'].append('ZEROS')
    
    # Repeating pattern?
    if len(set(chunk[:64])) < 10:
        analysis['patterns'].append('REPEATING')
    
    # High entropy (random data)?
    unique_bytes = len(set(chunk[:64]))
    if unique_bytes > 50:
        analysis['patterns'].append('HIGH_ENTROPY')
    
    return analysis


def compare_slots(filepath, slot_indices):
    """Compare multiple slots side by side"""
    print("=" * 100)
    print("ELDEN RING SAVE STRUCTURE ANALYZER")
    print("=" * 100)
    
    slots_data = {}
    
    # Read all slots
    for slot_idx in slot_indices:
        checksum, data = read_slot_data(filepath, slot_idx)
        header = parse_slot_header(data)
        
        slots_data[slot_idx] = {
            'checksum': checksum,
            'data': data,
            'header': header,
            'version': header['version']
        }
        
        print(f"\nSlot {slot_idx}:")
        print(f"  Version: {header['version']}")
        print(f"  Checksum: {checksum.hex()}")
        print(f"  Map ID: {header['map_id']}")
    
    print("\n" + "=" * 100)
    print("FINDING KEY STRUCTURES")
    print("=" * 100)
    
    # Key offsets we know from the parser
    KNOWN_OFFSETS = {
        'version': 0,
        'map_id': 4,
        'header_end': 32,
    }
    
    # Calculate where we expect things based on successful parsing
    # From the debug output, we know:
    # - Gaitems vary by version
    # - PlayerGameData is 432 bytes
    # - SPEffects is 208 bytes
    # - Equipment indexes is 292 bytes
    # - Held inventory is 36880 bytes
    # - More equipment is 2444 bytes
    # - FaceData is 303 bytes
    # - Storage inventory is 24592 bytes
    # Then comes Gestures...
    
    for slot_idx, slot_info in slots_data.items():
        data = slot_info['data']
        version = slot_info['version']
        
        print(f"\n--- Slot {slot_idx} (Version {version}) ---")
        
        # Calculate expected offset for gestures
        offset = 32  # After header
        
        # Gaitem map
        gaitem_count = 0x13FE if version <= 81 else 0x1400
        # Each gaitem is variable 8-21 bytes, but we need to actually parse them
        # For now, let's look at actual byte consumption from debug
        
        # Let's find where gestures might be by looking for gesture-like patterns
        print("\n  Searching for gesture patterns...")
        
        # Try different starting points
        search_starts = [
            (32 + 47000, "After ~47KB (slot 0 gaitem size)"),
            (32 + 41000, "After ~41KB (slot 1 gaitem size)"),  
            (32 + 42000, "After ~42KB (slot 2 gaitem size)"),
            (32 + 80000, "After ~80KB"),
            (32 + 100000, "After ~100KB"),
        ]
        
        for start_off, desc in search_starts:
            if start_off < len(data) - 1000:
                candidates = find_gestures_offset(data, start_off)
                if candidates:
                    print(f"\n  Found gesture-like patterns {desc}:")
                    for offset, values, score in candidates[:3]:
                        print(f"    Offset 0x{offset:08x}: {values[:4]} ... (score: {score}/8)")
    
    # Now let's do a detailed byte-by-byte comparison at key points
    print("\n" + "=" * 100)
    print("DETAILED COMPARISON AT KEY OFFSETS")
    print("=" * 100)
    
    # Compare at the point where we know things diverge
    # From debug: after storage inventory, before gestures
    compare_offsets = [
        0,      # Start
        32,     # After header
        65000,  # Approximate area where storage ends
        66000,
        67000,
        68000,
        69000,
        70000,
    ]
    
    for offset in compare_offsets:
        print(f"\n--- Offset 0x{offset:08x} ({offset} bytes) ---")
        for slot_idx, slot_info in slots_data.items():
            data = slot_info['data']
            if offset < len(data) - 32:
                chunk = data[offset:offset+32]
                u32s = [struct.unpack('<I', chunk[i:i+4])[0] for i in range(0, 32, 4)]
                print(f"  Slot {slot_idx} (v{slot_info['version']:3d}): {chunk.hex()[:64]}")
                print(f"                As u32s: {u32s}")
    
    # Write detailed dumps to files
    print("\n" + "=" * 100)
    print("WRITING DETAILED DUMPS")
    print("=" * 100)
    
    for slot_idx, slot_info in slots_data.items():
        data = slot_info['data']
        version = slot_info['version']
        
        output_file = f"slot_{slot_idx}_v{version}_dump.txt"
        with open(output_file, 'w') as f:
            f.write(f"Slot {slot_idx} - Version {version}\n")
            f.write("=" * 80 + "\n\n")
            
            # Write hex dump with annotations
            for offset in range(0, min(200000, len(data)), 16):
                hex_bytes = ' '.join(f'{b:02x}' for b in data[offset:offset+16])
                ascii_chars = ''.join(chr(b) if 32 <= b < 127 else '.' for b in data[offset:offset+16])
                f.write(f"{offset:08x}  {hex_bytes:<48}  {ascii_chars}\n")
        
        print(f"  Written: {output_file}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_save_structure.py <save_file> [slot_indices...]")
        print("\nExample:")
        print("  python analyze_save_structure.py ER0000.sl2 0 1 4")
        print("  This will analyze slots 0, 1, and 4")
        sys.exit(1)
    
    save_path = sys.argv[1]
    
    # Parse slot indices
    if len(sys.argv) > 2:
        slot_indices = [int(x) for x in sys.argv[2:]]
    else:
        # Default: analyze first 3 slots
        slot_indices = [0, 1, 2]
    
    if not Path(save_path).exists():
        print(f"Error: Save file not found: {save_path}")
        sys.exit(1)
    
    compare_slots(save_path, slot_indices)
    
    print("\n" + "=" * 100)
    print("ANALYSIS COMPLETE")
    print("=" * 100)
    print("\nCheck the slot_*_dump.txt files for detailed hex dumps.")
    print("Look for patterns in the 'gesture-like patterns' section above.")


if __name__ == "__main__":
    main()
