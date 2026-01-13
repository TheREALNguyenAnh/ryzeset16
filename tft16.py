import streamlit as st
import itertools

# --- 1. PAGE CONFIG & CSS ---
st.set_page_config(page_title="TFT Set 16 Optimizer", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        .block-container { padding: 1rem 1rem 0rem 1rem; }
        section[data-testid="stSidebar"] .block-container { padding-top: 1rem; }
        div.stButton > button {
            width: 100%; background-color: #FF4B4B; color: white; font-weight: bold; border: none;
        }
        div.stButton > button:hover { background-color: #FF0000; color: white; }
        .streamlit-expanderHeader { font-weight: bold; font-size: 1.1rem; }
        .stNumberInput input { padding-right: 0px; }
    </style>
""", unsafe_allow_html=True)

# --- GLOBAL LANGUAGE DICTIONARY ---
T = {
    "Tiếng Việt": {
        "title": "🧙‍♂️ TFT Mùa 16: World Runes Tool",
        "subtitle": "**Logic Mới:** Giới hạn Max 2 Shurima (Azir + Xerath).",
        "config": "⚙️ Cấu hình",
        "level": "Cấp độ (Level):",
        "btn_find": "🚀 TÌM ĐỘI HÌNH",
        "emb_region": "🌍 Ấn Vùng Đất (Region Emblems)",
        "emb_class": "🛡️ Ấn Tộc/Hệ (Class Emblems)",
        "donate_title": "### ☕ Ủng hộ Dev",
        "donate_btn": "☕ Buy Me a Coffee", 
        "select_modes": "📝 Chọn chế độ chạy (Để trống = Chạy tất cả):",
        "tabs": ["Giá Rẻ (Eco)", "Tiêu Chuẩn (Standard)", "EXODIA (Tối Thượng)", "🔓 MỞ KHÓA RYZE"],
        "mission_info": "🏆 **Nhiệm vụ:** Kích hoạt 4 Vùng Đất (Ưu tiên tìm từ 7 Slot & 0 Unlock).",
        "tag_basic": "🟢 **SHOP CƠ BẢN (CÓ SẴN)**",
        "tag_unlock": "🟠 **CẦN MỞ KHÓA ({})**",
        "err_unlock": "Không tìm thấy cách kích 4 vùng với số slot hiện tại.",
        "err_combat": "Không tìm thấy đội hình phù hợp. Hãy thử thêm Ấn hoặc đổi Level.",
        "spinner_unlock": "Đang quét các đội hình 7, 8, 9 slot...",
        "spinner_combat": "Đang tìm đồng đội cho Ryze...",
        "res_option": "Lựa chọn",
        "res_regions": "Vùng đất",
        "res_cost": "Vàng",
        "active": "**Kích hoạt:**",
        "slot_opt": "⚪ **Slot Tùy Chọn (Tự do)**", 
        "labels": [
            "👑 Lựa chọn 1: CÂN BẰNG NHẤT",
            "🌍 Lựa chọn 2: TỐI ĐA VÙNG ĐẤT",
            "🛡️ Lựa chọn 3: TỐI ĐA TỘC HỆ"
        ]
    },
    "English": {
        "title": "🧙‍♂️ TFT Set 16: World Runes Tool",
        "subtitle": "**New Logic:** Soft Cap at 2 Shurima (Azir + Xerath).",
        "config": "⚙️ Config",
        "level": "Level:",
        "btn_find": "🚀 FIND TEAMS",
        "emb_region": "🌍 Region Emblems",
        "emb_class": "🛡️ Class/Trait Emblems",
        "donate_title": "### ☕ Support Dev",
        "donate_btn": "☕ Buy Me a Coffee",
        "select_modes": "📝 Select Modes (Empty = Run All):",
        "tabs": ["Low Cost (Eco)", "Standard", "EXODIA", "WORLD RUNES MISSION"],
        "mission_info": "🏆 **Mission:** Activate 4 Regions (Prioritizes 7+ Slots & 0 Unlock).",
        "tag_basic": "🟢 **BASIC SHOP (AVAILABLE)**",
        "tag_unlock": "🟠 **REQUIRES {} UNLOCK(S)**",
        "err_unlock": "Cannot find 4 regions with current slots.",
        "err_combat": "No valid team found. Try adding Emblems or changing Level.",
        "spinner_unlock": "Scanning slot combinations...",
        "spinner_combat": "Finding teammates for Ryze...",
        "res_option": "Option",
        "res_regions": "Regions",
        "res_cost": "Gold",
        "active": "**Active:**",
        "slot_opt": "⚪ **Optional Slot (Free)**",
        "labels": [
            "👑 Option 1: BEST BALANCED",
            "🌍 Option 2: MAX REGIONS",
            "🛡️ Option 3: MAX TRAITS"
        ]
    }
}


# --- DATASETS ---
REGION_DATA = {
    "Bilgewater":   {"thresholds": [3, 5, 7, 10]}, "Demacia": {"thresholds": [3, 5, 7, 11]},
    "Freljord":     {"thresholds": [3, 5, 7]}, "Ionia": {"thresholds": [3, 5, 7, 10]},
    "Ixtal":        {"thresholds": [3, 5, 7]}, "Noxus": {"thresholds": [3, 5, 7, 10]},
    "Piltover":     {"thresholds": [2, 4, 6]}, "Shadow Isles": {"thresholds": [2, 3, 4, 5]},
    "Shurima":      {"thresholds": [2, 3, 4, 6]}, "Targon": {"thresholds": [1, 2, 3, 4]}, 
    "Void":         {"thresholds": [2, 4, 6, 9]}, "Yordle": {"thresholds": [2, 4, 6, 8]},
    "Zaun":         {"thresholds": [3, 5, 7]}
}

CLASS_DATA = {
    "Bruiser": [2, 4, 6], "Defender": [2, 4, 6], "Invoker": [2, 4, 6],
    "Slayer": [2, 4, 6], "Gunslinger": [2, 4, 6], "Arcanist": [2, 4, 6],
    "Warden": [2, 3, 4, 5], "Juggernaut": [2, 4, 6], "Longshot": [2, 3, 4, 5],
    "Quickstriker": [2, 3, 4, 5], "Disruptor": [2, 4], "Vanquisher": [2, 3, 4, 5],
    "Darkin": [1, 2, 3],
    "Heroic": [1], "The Boss": [1], "Emperor": [1], "Ascendant": [1], 
    "Star Forger": [1], "Caretaker": [1], "Rune Mage": [1], "Assimilator": [1],
    "Huntress": [1], "Glutton": [1], "Blacksmith": [1], "Soulbound": [1],
    "Eternal": [1], "Dragonborn": [1], "Chronokeeper": [1], "Dark Child": [1],
    "Harvester": [1], "HexMech": [1], "Chainbreaker": [1], "Riftscourge": [1],
    "Immortal": [1]
}

UNIQUE_TRAITS = list(CLASS_DATA.keys())[-22:]

GALIO_UNIT = {"name": "Galio", "traits": ["Demacia", "Invoker", "Heroic"], "cost": 5, "diff": 3, "role": "tank"}

# --- UNIT LISTS ---
STANDARD_UNITS = [
    # 1 COST
    {"name": "Anivia", "traits": ["Freljord", "Invoker"], "cost": 1, "diff": 1, "role": "carry"},
    {"name": "Blitzcrank", "traits": ["Zaun", "Juggernaut"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Briar", "traits": ["Noxus", "Slayer", "Juggernaut"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Caitlyn", "traits": ["Piltover", "Longshot"], "cost": 1, "diff": 1, "role": "carry"},
    {"name": "Illaoi", "traits": ["Bilgewater", "Bruiser"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Jarvan IV", "traits": ["Demacia", "Defender"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Jhin", "traits": ["Ionia", "Gunslinger"], "cost": 1, "diff": 1, "role": "carry"},
    {"name": "Kog'Maw", "traits": ["Void", "Arcanist", "Longshot"], "cost": 1, "diff": 1, "role": "carry"},
    {"name": "Lulu", "traits": ["Yordle", "Arcanist"], "cost": 1, "diff": 1, "role": "supp"},
    {"name": "Qiyana", "traits": ["Ixtal", "Slayer"], "cost": 1, "diff": 1, "role": "carry"},
    {"name": "Rumble", "traits": ["Yordle", "Defender"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Shen", "traits": ["Ionia", "Bruiser"], "cost": 1, "diff": 1, "role": "tank"},
    {"name": "Sona", "traits": ["Demacia", "Invoker"], "cost": 1, "diff": 1, "role": "supp"},
    {"name": "Viego", "traits": ["Shadow Isles", "Quickstriker"], "cost": 1, "diff": 1, "role": "carry"},

    # 2 COST
    {"name": "Aphelios", "traits": ["Targon"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Ashe", "traits": ["Freljord", "Quickstriker"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Cho'Gath", "traits": ["Void", "Juggernaut"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Ekko", "traits": ["Zaun", "Disruptor"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Neeko", "traits": ["Ixtal", "Arcanist", "Defender"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Rek'Sai", "traits": ["Void", "Vanquisher"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Sion", "traits": ["Noxus", "Bruiser"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Teemo", "traits": ["Yordle", "Longshot"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Tristana", "traits": ["Yordle", "Gunslinger"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Twisted Fate", "traits": ["Bilgewater", "Quickstriker"], "cost": 2, "diff": 1, "role": "carry"},
    {"name": "Vi", "traits": ["Piltover", "Zaun", "Defender"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Xin Zhao", "traits": ["Demacia", "Ionia", "Warden"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Yasuo", "traits": ["Ionia", "Slayer"], "cost": 2, "diff": 1, "role": "carry"},

    # 3 COST
    {"name": "Ahri", "traits": ["Ionia", "Arcanist"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Dr. Mundo", "traits": ["Zaun", "Bruiser"], "cost": 3, "diff": 1, "role": "tank"},
    {"name": "Draven", "traits": ["Noxus", "Quickstriker"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Gangplank", "traits": ["Bilgewater", "Slayer", "Vanquisher"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Jinx", "traits": ["Zaun", "Gunslinger"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Leona", "traits": ["Targon"], "cost": 3, "diff": 1, "role": "tank"},
    {"name": "Loris", "traits": ["Piltover", "Warden"], "cost": 3, "diff": 1, "role": "tank"},
    {"name": "Malzahar", "traits": ["Void", "Disruptor"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Milio", "traits": ["Ixtal", "Invoker"], "cost": 3, "diff": 1, "role": "supp"},
    {"name": "Nautilus", "traits": ["Bilgewater", "Juggernaut", "Warden"], "cost": 3, "diff": 1, "role": "tank"},
    {"name": "Sejuani", "traits": ["Freljord", "Defender"], "cost": 3, "diff": 1, "role": "tank"},
    {"name": "Vayne", "traits": ["Demacia", "Longshot"], "cost": 3, "diff": 1, "role": "carry"},
    {"name": "Zoe", "traits": ["Targon"], "cost": 3, "diff": 1, "role": "carry"},

    # 4 COST
    {"name": "Taric", "traits": ["Targon"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Ambessa", "traits": ["Noxus", "Vanquisher"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Bel'Veth", "traits": ["Void", "Slayer"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Braum", "traits": ["Freljord", "Warden"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Garen", "traits": ["Demacia", "Defender"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Lissandra", "traits": ["Freljord", "Invoker"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Lux", "traits": ["Demacia", "Arcanist"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Miss Fortune", "traits": ["Bilgewater", "Gunslinger"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Seraphine", "traits": ["Piltover", "Disruptor"], "cost": 4, "diff": 2, "role": "supp"},
    {"name": "Swain", "traits": ["Noxus", "Arcanist", "Juggernaut"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Wukong", "traits": ["Ionia", "Bruiser"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Yunara", "traits": ["Ionia", "Quickstriker"], "cost": 4, "diff": 2, "role": "carry"},

    # 5 COST
    {"name": "Aatrox", "traits": ["Darkin", "Slayer"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Annie", "traits": ["Dark Child", "Arcanist"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Azir", "traits": ["Shurima", "Emperor", "Disruptor"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Fiddlesticks", "traits": ["Harvester", "Vanquisher"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Kindred", "traits": ["Eternal", "Quickstriker"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Lucian & Senna", "traits": ["Soulbound", "Gunslinger"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Ornn", "traits": ["Blacksmith", "Warden"], "cost": 5, "diff": 3, "role": "tank"},
    {"name": "Shyvana", "traits": ["Dragonborn", "Juggernaut"], "cost": 5, "diff": 3, "role": "tank"},
    {"name": "Zilean", "traits": ["Chronokeeper", "Invoker"], "cost": 5, "diff": 3, "role": "supp"}
]

UNLOCKABLE_UNITS = [
    # 2 COST
    {"name": "Poppy", "traits": ["Demacia", "Yordle", "Juggernaut"], "cost": 2, "diff": 1, "role": "tank"},
    {"name": "Bard", "traits": ["Caretaker"], "cost": 2, "diff": 2, "role": "supp"},
    {"name": "Orianna", "traits": ["Piltover", "Invoker"], "cost": 2, "diff": 2, "role": "supp"},
    {"name": "Graves", "traits": ["Bilgewater", "Gunslinger"], "cost": 2, "diff": 2, "role": "carry"},
    {"name": "Yorick", "traits": ["Shadow Isles", "Warden"], "cost": 2, "diff": 2, "role": "tank"},
    {"name": "Tryndamere", "traits": ["Freljord", "Slayer"], "cost": 2, "diff": 2, "role": "carry"},
    
    # 3 COST
    {"name": "Kennen", "traits": ["Ionia", "Yordle", "Defender"], "cost": 3, "diff": 2, "role": "tank"},
    {"name": "Kobuko & Yuumi", "traits": ["Yordle", "Bruiser", "Invoker"], "cost": 3, "diff": 2, "role": "tank"},
    {"name": "Darius", "traits": ["Noxus", "Defender"], "cost": 3, "diff": 2, "role": "tank"},
    {"name": "Gwen", "traits": ["Shadow Isles", "Disruptor"], "cost": 3, "diff": 2, "role": "carry"},
    {"name": "LeBlanc", "traits": ["Noxus", "Invoker"], "cost": 3, "diff": 2, "role": "carry"},
    
    # 4 COST
    {"name": "Fizz", "traits": ["Bilgewater", "Yordle"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Warwick", "traits": ["Zaun", "Quickstriker"], "cost": 4, "diff": 1, "role": "carry"},
    {"name": "Nidalee", "traits": ["Ixtal", "Huntress"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Skarner", "traits": ["Ixtal"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Rift Herald", "traits": ["Void", "Bruiser"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Singed", "traits": ["Zaun", "Juggernaut"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Kai'Sa", "traits": ["Void", "Longshot", "Assimilator"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Kalista", "traits": ["Shadow Isles", "Vanquisher"], "cost": 4, "diff": 2, "role": "carry"},
    {"name": "Nasus", "traits": ["Shurima"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Renekton", "traits": ["Shurima"], "cost": 4, "diff": 2, "role": "tank"},
    {"name": "Veigar", "traits": ["Yordle", "Arcanist"], "cost": 4, "diff": 3, "role": "carry"},
    {"name": "Diana", "traits": ["Targon"], "cost": 4, "diff": 2, "role": "carry"},
    
    # 5 COST
    {"name": "Sett", "traits": ["Ionia", "The Boss"], "cost": 5, "diff": 3, "role": "tank"},
    {"name": "Volibear", "traits": ["Freljord", "Bruiser"], "cost": 5, "diff": 3, "role": "tank"},
    {"name": "Xerath", "traits": ["Shurima", "Ascendant"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Mel", "traits": ["Noxus", "Disruptor"], "cost": 5, "diff": 3, "role": "carry"},
    {"name": "Ziggs", "traits": ["Zaun", "Yordle", "Longshot"], "cost": 5, "diff": 3, "role": "carry"},
]

ALL_UNITS = STANDARD_UNITS + UNLOCKABLE_UNITS

# --- ALGORITHM 1: UNLOCK MISSION (PRIORITY: 0 UNLOCKS > LOW SLOTS > LOW COST) ---
@st.cache_data(show_spinner=False)
def solve_unlock_mission(slots, user_emblems):
    candidates = []
    limit_max = 300000 
    
    region_units = [u for u in ALL_UNITS if any(t in REGION_DATA for t in u['traits'])]
    
    def get_unlock_score(u):
        score = 0
        if any(u['name'] == su['name'] for su in STANDARD_UNITS):
            score += 5000
        r_count = sum(1 for t in u['traits'] if t in REGION_DATA)
        if r_count >= 2: score += 1000
        for t in u['traits']:
            if t in user_emblems: score += 100
            if t == "Targon": score += 50 
        score += (10 - u['cost'])
        return score

    region_units.sort(key=get_unlock_score, reverse=True)
    
    standard_best = [u for u in region_units if any(u['name'] == su['name'] for su in STANDARD_UNITS)][:35]
    unlock_best = [u for u in region_units if any(u['name'] == uu['name'] for uu in UNLOCKABLE_UNITS)][:15]
    search_pool = standard_best + unlock_best

    # --- LOGIC: SEARCH RANGE BASED ON PLAYER LEVEL ---
    # Level 4: [4]
    # Level 5: [4, 5]
    # Level 6: [4, 5, 6]
    # Level 7: [5, 6, 7]
    # Level 8: [6, 7, 8]
    if slots == 4:
        search_sizes = [4]
    elif slots == 5:
        search_sizes = [4, 5]
    elif slots == 6:
        search_sizes = [4, 5, 6]
    elif slots == 7:
        search_sizes = [5, 6, 7]
    else:  # slots == 8
        search_sizes = [6, 7, 8]

    for current_size in search_sizes:
        loop_count = 0 
        
        # Biến cờ để kiểm tra xem đã tìm được đội hình "hoàn hảo" (0 unlock) ở size này chưa
        found_zero_unlock_at_this_size = False

        for team in itertools.combinations(search_pool, current_size):
            loop_count += 1
            if loop_count > limit_max: break
            if len(set([u['name'] for u in team])) < len(team): continue

            traits = {}
            total_cost = 0
            unlock_count = 0
            
            for u in team:
                total_cost += u.get('cost', 1)
                if any(u['name'] == ul['name'] for ul in UNLOCKABLE_UNITS):
                    unlock_count += 1
                for t in u['traits']:
                    traits[t] = traits.get(t, 0) + 1
                    
            for emb, count in user_emblems.items():
                traits[emb] = traits.get(emb, 0) + count
                
            active_regions = 0
            active_list = []
            active_regions_names = []
            
            for r, data in REGION_DATA.items():
                if traits.get(r, 0) >= data['thresholds'][0]:
                    active_regions += 1
                    active_list.append(f"{r}({traits[r]})")
                    active_regions_names.append(r)
            
            if active_regions >= 4:
                active_regions_names.sort()
                region_sig = "-".join(active_regions_names)
                
                candidates.append({
                    "team": list(team),
                    "active_count": active_regions,
                    "cost": total_cost,
                    "regions": active_list,
                    "unlock_count": unlock_count,
                    "region_sig": region_sig
                })
                
                if unlock_count == 0:
                    found_zero_unlock_at_this_size = True

                if len(candidates) >= 200: break
        
        # --- LOGIC QUYẾT ĐỊNH DỪNG VÒNG LẶP ---
        # Nếu tìm được đội hình 0 unlock ở bất kỳ size nào (kể cả 7), ta ưu tiên nó nhất và dừng tìm kiếm ở các size lớn hơn.
        # Vì ưu tiên tối thượng là: 0 Unlock. Sau đó mới đến Slot.
        # Nếu tìm được 7 slot (0 unlock) -> Dừng.
        # Nếu tìm được 7 slot (có unlock) -> Chạy tiếp 8 slot.
        # Nếu tìm được 8 slot (0 unlock) -> Dừng.
        if found_zero_unlock_at_this_size:
            break
        
    candidates.sort(key=lambda x: (x['unlock_count'], len(x['team']), -x['active_count'], x['cost']))
    
    # --- BỘ LỌC ĐA DẠNG ---
    final_results = []
    seen_sigs = set()
    
    for cand in candidates:
        if cand['region_sig'] not in seen_sigs:
            final_results.append(cand)
            seen_sigs.add(cand['region_sig'])
        if len(final_results) >= 5: break
    
    if len(final_results) < 5:
        remaining_slots = 5 - len(final_results)
        for cand in candidates:
            if cand not in final_results:
                final_results.append(cand)
                remaining_slots -= 1
            if remaining_slots <= 0: break
            
    final_results.sort(key=lambda x: (x['unlock_count'], len(x['team']), -x['active_count'], x['cost']))
    
    return final_results

# --- ALGORITHM 2: STANDARD OPTIMIZER (CACHED) ---
@st.cache_data(show_spinner=False)
def build_synergy_pool(base_pool, user_emblems, prioritize_strength=False):
    # CHẤM ĐIỂM TIỀM NĂNG (UTILITY SCORE) CHO TỪNG TƯỚNG
    # Mục tiêu: Tìm ra những tướng có khả năng kết nối tốt nhất (Bridge Units)
    
    scored_pool = []
    # Kiểm tra xem có Azir trong pool không (để kích hoạt Buddy System)
    has_azir_in_base = any(u['name'] == "Azir" for u in base_pool)

    for u in base_pool:
        score = 0
        traits = u['traits']
        
        # 1. ƯU TIÊN TỐI THƯỢNG: Trùng Ấn người dùng đang có
        for t in traits:
            if t in user_emblems:
                score += 100
        
        # 2. ƯU TIÊN SỐ 2: Tướng Đa Hệ (3 Tộc/Hệ trở lên)
        if len(traits) >= 3:
            score += 50
            
        # 3. ƯU TIÊN SỐ 3: Tộc Vùng Đất (Region Traits)
        has_region = False
        for t in traits:
            if t in REGION_DATA:
                score += 30
                has_region = True
        
        # 4. SỨC MẠNH CƠ BẢN (Cost)
        if u['cost'] >= 4: score += 20
        elif u['cost'] == 3: score += 10
        
        # Targon luôn hữu dụng
        if "Targon" in traits: score += 15

        # --- LOGIC MỚI: BUDDY SYSTEM (CẶP BÀI TRÙNG) ---
        # Nếu có Azir, buộc phải kéo Xerath lên top để tính toán
        if has_azir_in_base and u['name'] == "Xerath":
            score += 200 # Cộng cực lớn để đảm bảo lọt top 45

        scored_pool.append({"unit": u, "score": score})

    # Sắp xếp theo điểm tiềm năng giảm dần
    scored_pool.sort(key=lambda x: x['score'], reverse=True)
    
    # Lấy Top 45 tướng hữu dụng nhất
    final_pool = [item['unit'] for item in scored_pool[:45]]
    
    # Sort lại theo Cost để itertools ưu tiên xếp tướng đắt làm trụ cột trước
    final_pool.sort(key=lambda x: x['cost'], reverse=True)
        
    return final_pool

@st.cache_data(show_spinner=False)
def solve_three_strategies(pool, slots, user_emblems, prioritize_strength=False):
    
    final_pool = build_synergy_pool(pool, user_emblems, prioritize_strength)

    limit_max = 2000000
    loop_count = 0
    candidates = []

    search_sizes = [slots]
    if any(u['name'] == "Annie" for u in final_pool):
        search_sizes.append(slots - 1)

    for size in search_sizes:
        for team in itertools.combinations(final_pool, size):
            loop_count += 1
            if loop_count > limit_max: break
            if len(set([u['name'] for u in team])) < len(team): continue

            slots_used = 0
            has_annie = False
            for u in team:
                if u['name'] == "Annie":
                    slots_used += 2
                    has_annie = True
                else:
                    slots_used += 1
            
            if slots_used > slots: continue
            if size == (slots - 1) and not has_annie: continue

            traits = {}
            tank_count = 0
            team_total_cost = 0 
            names = [u['name'] for u in team]
            
            for u in team:
                team_total_cost += u.get('cost', 1)
                if u.get('role') == 'tank': tank_count += 1
                for t in u['traits']:
                    traits[t] = traits.get(t, 0) + 1
                if u['name'] == "Annie": traits['Arcanist'] = traits.get('Arcanist', 0) + 1
                    
            for emb, count in user_emblems.items():
                traits[emb] = traits.get(emb, 0) + count
            
            has_galio = False
            final_team = list(team)
            if traits.get("Demacia", 0) >= 6:
                has_galio = True
                final_team.append(GALIO_UNIT)
                tank_count += 1
                for t in GALIO_UNIT['traits']: traits[t] = traits.get(t, 0) + 1
            
            r_score = 0
            active_regions_set = set()
            unused_emblem_penalty = 0
            
            # --- TÍNH ĐIỂM VÙNG ĐẤT (REGION SCORING) ---
            for r, data in REGION_DATA.items():
                count = traits.get(r, 0)
                if count >= data['thresholds'][0]: 
                    tier_index = 0
                    for i, t_val in enumerate(data['thresholds']):
                        if count >= t_val: tier_index = i + 1
                        else: break
                    
                    r_score += (tier_index * 2) 
                    active_regions_set.add(r)
                    
                    current_tier_threshold = 0
                    for t in data['thresholds']:
                        if count >= t: current_tier_threshold = t
                        else: break
                    if count > current_tier_threshold: unused_emblem_penalty -= 2 
                elif user_emblems.get(r, 0) > 0:
                    unused_emblem_penalty -= 10 
            
            final_r = r_score + (5 if has_galio else 0) 
            
            if final_r == 0: continue

            # --- TÍNH ĐIỂM HỆ NGHỀ (CLASS SCORING) ---
            c_score = 0
            unique_bonus = 0 
            active_classes_set = set()
            
            for cl, thresholds in CLASS_DATA.items():
                if cl in UNIQUE_TRAITS: continue # Bỏ qua Unique traits
                
                if traits.get(cl, 0) >= thresholds[0]: 
                    c_score += 1 
                    active_classes_set.add(cl)

            # --- BỘ LỌC DEAD WEIGHT (ĐÃ FIX LOGIC) ---
            dead_weight_count = 0
            useless_unit_penalty = 0
            
            for u in final_team:
                if u['name'] in ["Ryze", "Galio", "Taric", "Ornn"]: continue
                
                is_active = False
                for t in u['traits']:
                    if t in active_regions_set or t in active_classes_set:
                        is_active = True
                        break
                    # Giữ lại tướng 5 tiền Unique (Aatrox, Belveth...)
                    if t in UNIQUE_TRAITS and u['cost'] == 5:
                        is_active = True
                        break
                
                if not is_active:
                    dead_weight_count += 1
                    useless_unit_penalty -= 1000 
            
            if dead_weight_count > 1: continue

            final_r_penalty = 0
            if len(active_regions_set) < 2 and slots >= 7: 
                final_r_penalty = -500

            # --- SHURIMA LIMITER (Logic User Yêu Cầu) ---
            shurima_penalty = 0
            shurima_count = traits.get("Shurima", 0)
            if shurima_count > 2:
                shurima_penalty -= 2500 # Phạt nặng để ưu tiên giữ ở mốc 2
                if shurima_count >= 4:
                    shurima_penalty -= 10000 # Phạt cực nặng (Bất khả thi)

            # --- XỬ LÝ TARGON & NERF FIZZ ---
            targon_c = traits.get("Targon", 0)
            if targon_c == 1: 
                useless_unit_penalty += 100 # Thưởng lớn nếu chỉ có 1 Targon
            elif targon_c > 1: 
                # PHẠT CỰC NẶNG (-2000) ĐỂ GHI ĐÈ ĐIỂM CỘNG TỪ REGION SCORING
                useless_unit_penalty -= 2000 
            elif targon_c == 0:
                useless_unit_penalty -= 50

            # Nếu có Fizz trong Exodia mode mà không kích Bilgewater, trừ nặng
            if prioritize_strength and "Fizz" in names and traits.get("Bilgewater", 0) < 3:
                useless_unit_penalty -= 300
            
            # --- UNIQUE TRAITS (ĐÃ FIX LỖI UnboundLocalError) ---
            for u_trait in UNIQUE_TRAITS:
                 if traits.get(u_trait, 0) >= 1:
                    if u_trait == "Blacksmith": unique_bonus += 0.5
                    else:
                        unit_with_trait = next((u for u in final_team if u_trait in u['traits']), None)
                        if unit_with_trait:
                            is_supported = False
                            for other_t in unit_with_trait['traits']:
                                if other_t in active_regions_set or other_t in active_classes_set: is_supported = True
                            
                            # CHỈ CỘNG ĐIỂM, KHÔNG APPEND VÀO LIST
                            if is_supported: unique_bonus += 0.5

            balance_penalty = 0
            if tank_count < 2 and not prioritize_strength: balance_penalty = -10 
            
            targon_bonus = 0
            if "Taric" in names: targon_bonus += 20
            annie_penalty = -12 if "Annie" in names else 0
            
            strength_score = 0
            if prioritize_strength:
                strength_score = team_total_cost * 0.1

            synergy_density = (len(active_regions_set) * 10) + (len(active_classes_set) * 5)

            # --- POWER PAIRS: AZIR + XERATH (NEW) ---
            combo_bonus = 0
            if "Azir" in names and "Xerath" in names:
                combo_bonus += 5000 # Boost cực đại
            # Nếu có Azir mà thiếu Xerath (trong tab Exodia), trừ điểm
            elif "Azir" in names and "Xerath" not in names and prioritize_strength:
                combo_bonus -= 500

            smart_score = (final_r * 200.0) + \
                          (c_score * 40.0) + \
                          (unique_bonus * 5.0) + \
                          combo_bonus + \
                          strength_score + \
                          synergy_density + \
                          balance_penalty + unused_emblem_penalty + targon_bonus + annie_penalty + \
                          useless_unit_penalty + final_r_penalty + shurima_penalty
            
            # --- TẠO DANH SÁCH HIỂN THỊ (FINAL FORMATTING) ---
            r_list_fmt = [f"{r}({traits[r]})" for r in REGION_DATA if traits.get(r,0) >= REGION_DATA[r]['thresholds'][0]]
            c_list_fmt = [f"{c}({traits[c]})" for c in CLASS_DATA if traits.get(c,0) >= CLASS_DATA[c][0] and c not in UNIQUE_TRAITS]
            if traits.get("Darkin", 0) >= 1: c_list_fmt.append(f"Darkin({traits['Darkin']})")
            
            # Thêm Unique Traits vào hiển thị
            for u_trait in UNIQUE_TRAITS:
                if traits.get(u_trait, 0) >= 1:
                     if u_trait == "Blacksmith": c_list_fmt.append("Blacksmith")
                     else:
                        unit_with_trait = next((u for u in final_team if u_trait in u['traits']), None)
                        if unit_with_trait:
                            is_supported = False
                            for other_t in unit_with_trait['traits']:
                                if other_t in active_regions_set or other_t in active_classes_set: is_supported = True
                            if is_supported: c_list_fmt.append(u_trait)

            # Đếm số lượng Region Active THỰC TẾ (dùng để sort Option 2)
            real_active_regions = len(active_regions_set)

            candidates.append({
                "team": final_team,
                "r_score": final_r,
                "c_score": c_score,
                "smart_score": smart_score,
                "r_list": r_list_fmt,
                "c_list": c_list_fmt,
                "galio": has_galio,
                "tanks": tank_count,
                "real_active_regions": real_active_regions 
            })

    if not candidates: return []
    
    candidates.sort(key=lambda x: x['smart_score'], reverse=True)
    opt1 = candidates[0]
    
    # --- LOGIC OPTION 2: MAX REGIONS (ĐÃ FIX) ---
    # Ưu tiên số lượng Vùng Đất thực tế (real_active_regions) lên hàng đầu
    candidates.sort(key=lambda x: (x['real_active_regions'], x['smart_score']), reverse=True)
    opt2 = candidates[0]
    if opt2['team'] == opt1['team']:
        for cand in candidates:
            if cand['team'] != opt1['team']:
                opt2 = cand
                break
    
    candidates.sort(key=lambda x: (len(x['c_list']), x['smart_score']), reverse=True)
    opt3 = candidates[0]
    for cand in candidates:
        if cand['team'] != opt1['team'] and cand['team'] != opt2['team']:
            opt3 = cand
            break
    
    return [opt1, opt2, opt3]

# --- UI ---
st.title("🧙‍♂️ TFT Set 16: World Runes Tool")
st.markdown("**Strategic Diversity:** Full Optimization.")

with st.sidebar:
    st.header("⚙️ Config")
    
    # --- MULTI-LANGUAGE SELECTOR ---
    lang_options = ["English", "Tiếng Việt"] # English Default
    lang_choice = st.selectbox("🌐 Language", lang_options)
    
    t = T[lang_choice] # Current Language

    # --- LEVEL SELECTION ---
    level_options = {
        "4 Slots": 4,
        "5 Slots": 5,
        "6 Slots": 6,
        "7 Slots": 7,
        "8 Slots": 8
    }
    level_choice = st.selectbox(t["level"], level_options.keys())
    level = level_options[level_choice]
    st.markdown(f"**Slots Available:** {level} 🟡", unsafe_allow_html=True)
    st.markdown("---")
    run = st.button(t["btn_find"], type="primary")
    st.markdown("---")
    
    # --- MERGED EMBLEM INPUTS ---
    r_emblems = {}
    c_emblems = {}
    
    with st.expander(t["emb_region"], expanded=False): # Default Closed
        cols = st.columns(2)
        keys = sorted(REGION_DATA.keys())
        for i, k in enumerate(keys):
            v = cols[i%2].number_input(k, 0, 3, key=f"r_{k}")
            if v: r_emblems[k] = v
            
    with st.expander(t["emb_class"], expanded=False):
        cols = st.columns(2)
        keys = sorted(list(CLASS_DATA.keys())) 
        for i, k in enumerate(keys):
            v = cols[i%2].number_input(k, 0, 3, key=f"c_{k}")
            if v: c_emblems[k] = v
            
    user_emblems = {**r_emblems, **c_emblems}

    # --- PAYPAL / BMC DONATE ---
    st.markdown("---")
    st.markdown(t["donate_title"])
    donate_url = "https://buymeacoffee.com/nguyenanh"
    
    st.markdown(f"""
        <a href="{donate_url}" target="_blank" style="text-decoration: none;">
            <div style="
                background-color: #0070BA; 
                color: white; 
                padding: 12px 20px; 
                border-radius: 25px; 
                text-align: center; 
                font-weight: bold;
                font-size: 16px;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
                transition: 0.3s;
                display: flex;
                justify-content: center;
                align-items: center;
                margin: 0 auto;
            ">
                {t["donate_btn"]}
            </div>
        </a>
    """, unsafe_allow_html=True)

if run:
    slots_for_unlock = level
    
    with st.spinner(t["spinner_unlock"]):
        res = solve_unlock_mission(slots_for_unlock, user_emblems)
    
    if res:
        st.subheader(t["tabs"][3])
        for i, data in enumerate(res):
            expanded = (i==0)
            u_count = data['unlock_count']
            if u_count == 0: 
                tag = t["tag_basic"]
            else: 
                tag = t["tag_unlock"].format(u_count)
            title = f"{tag} | {t['res_option']} {i+1}: {data['active_count']} {t['res_regions']} ({t['res_cost']}: {data['cost']}🟡)"
            with st.expander(title, expanded=expanded):
                st.success(f"{t['active']} {', '.join(data['regions'])}")
                cols = st.columns(2)
                active_region_names = [r.split('(')[0] for r in data['regions']]
                idx = 1
                for u in data['team']:
                    col = cols[(idx-1) % 2]
                    traits_html = []
                    for tr in u['traits']:
                        if tr in active_region_names: 
                            traits_html.append(f"<span style='color:#2E7D32'><b>{tr}</b></span>")
                        else: 
                            traits_html.append(f"<span style='color:#555'>{tr}</span>")
                    unit_name_display = u['name']
                    if any(u['name'] == ul['name'] for ul in UNLOCKABLE_UNITS): 
                        unit_name_display += " 🔒"
                    col.markdown(f"{idx}. **{unit_name_display}** ({u['cost']}🟡) : {' '.join(traits_html)}", unsafe_allow_html=True)
                    idx += 1
                
                # Fill remaining slots
                while idx <= slots_for_unlock:
                    col = cols[(idx-1) % 2]
                    col.markdown(f"{idx}. {t['slot_opt']}", unsafe_allow_html=True)
                    idx += 1
    else:
        st.error(t["err_unlock"])

elif not run:
    st.info("👈 Select Options -> Click FIND TEAMS")
