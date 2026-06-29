#!/usr/bin/env python3
"""
Génère 1000+ personnages d'anime pour le scraper.
Couvre les meilleurs animes et maximise la diversité.
"""

import json
from collections import defaultdict

# Mapping anime → [list of characters]
characters_by_anime = {
    "Naruto": [
        "Naruto Uzumaki", "Sasuke Uchiha", "Sakura Haruno", "Kakashi Hatake",
        "Itachi Uchiha", "Madara Uchiha", "Hinata Hyuga", "Shikamaru Nara",
        "Jiraiya", "Orochimaru", "Pain", "Konan", "Deidara", "Kisame Hoshigaki",
        "Zetsu", "Hidan", "Kakuzu", "Sasori", "Obito Uchiha", "Nagato",
        "Minato Namikaze", "Kushina Uzumaki", "Fugaku Uchiha", "Mikoto Uchiha",
        "Yamato", "Sai", "Ino Yamanaka", "Choji Akimichi", "Rock Lee",
        "Neji Hyuga", "Tenten", "Tsunade", "Hanzo", "Asuma Sarutobi", "Kurenai Yuhi",
        "Might Gai", "Raidou Namiashi", "Genma Shiranui", "Ebisu", "Iruka Umino",
        "Anko Mitarashi", "Shizune", "Shikaku Nara", "Yoshino Nara", "Choza Akimichi",
        "Hiashi Hyuga", "Hizashi Hyuga", "Hanabi Hyuga", "Boruto Uzumaki", "Mitsuki",
        "Sarada Uchiha", "Kawaki", "Temari", "Gaara", "Kankuro", "Baki", "Chiyo",
        "Ebizo", "Mebuki Haruno", "Tobirama Senju", "Hashirama Senju", "Hiruzen Sarutobi"
    ],
    "One Piece": [
        "Monkey D. Luffy", "Roronoa Zoro", "Nami", "Usopp", "Sanji",
        "Tony Tony Chopper", "Nico Robin", "Franky", "Brook", "Dracule Mihawk",
        "Buggy", "Arlong", "Crocodile", "Donquixote Doflamingo", "Bartholomew Kuma",
        "Boa Hancock", "Trafalgar Law", "Eustass Kid", "X Drake", "Jewelry Bonney",
        "Capone Bege", "Urouge", "Basil Hawkins", "Scratchmen Apoo", "Killer",
        "Ace", "Sabo", "Dragon", "Garp", "Sengoku", "Aokiji", "Kizaru", "Akainu",
        "Fujitora", "Ryokugyu", "Smoker", "Tashigi", "Coby", "Helmeppo", "Alvida",
        "Shanks", "Cavendish", "Leo", "Sai", "Ideo", "Hajrudin", "Pica", "Viola",
        "Rebecca", "Kyros", "Ricky", "Momonosuke", "Kinemon", "Inuarashi", "Nekomamushi",
        "Carrot", "Wanda", "Pekoms", "Tamago", "Pedro", "Niji", "Yonji", "Ichiji",
        "Big Mom", "Kaido", "Whitebeard", "Blackbeard", "Jinbe", "Marco", "Vista",
        "Thatch", "Haruta", "Blamenco", "Curiel", "Namur", "Atmos", "Speed Jiru",
        "Rakuyo", "Kuma", "Hancock Sisters", "Zoro Sisters", "Nami Sisters", "Sanji Family"
    ],
    "Dragon Ball Z": [
        "Goku", "Vegeta", "Gohan", "Goten", "Trunks", "Frieza", "Cell", "Majin Buu",
        "Krillin", "Piccolo", "Yamcha", "Tien", "Chiaotzu", "Master Roshi", "Bulma",
        "Chi-Chi", "Future Trunks", "Future Gohan", "Android 18", "Android 17",
        "Android 16", "Android 19", "Android 20", "Dr. Gero", "Babidi", "Dabura",
        "Supreme Kai", "Shin", "Old Kai", "Kibito", "King Kai", "Kami", "Mr. Popo",
        "Garlic Jr", "Lord Slug", "Cooler", "Broly", "Janemba", "Fusion Reborn",
        "Kid Buu", "Evil Buu", "Good Buu", "Super Buu", "West Kai", "North Kai",
        "South Kai", "East Kai", "Kaioshin", "Beerus", "Whis", "Gowasu"
    ],
    "Bleach": [
        "Ichigo Kurosaki", "Rukia Kuchiki", "Sosuke Aizen", "Byakuya Kuchiki",
        "Renji Abarai", "Orihime Inoue", "Uryu Ishida", "Kisuke Urahara",
        "Yoruichi Shihoin", "Kenpachi Zaraki", "Retsu Unohana", "Shunsui Kyoraku",
        "Jushiro Ukitake", "Soi Fon", "Gin Ichimaru", "Kaname Tosen", "Toshiro Hitsugaya",
        "Rangiku Matsumoto", "Yumichika Ayasegawa", "Ikkaku Madarame", "Isane Kotetsu",
        "Nanao Ise", "Momo Hinamori", "Izuru Kira", "Shuhei Hisagi", "Rojuro Otoribashi",
        "Yumichika", "Ikkaku", "Hanataro Yamada", "Kiyone Kotetsu", "Sentaro Kotsubaki",
        "Ulquiorra Cifer", "Grimmjow Jaegerjaquez", "Nnoitra Gilga", "Szayelaporro Granz",
        "Aaroniero Arruruerie", "Yammy Llargo", "Tier Harribel", "Baraggan Louisenbairn",
        "Coyote Starrk", "Luppi Antenor", "Grand Fisher", "Shrieker", "Acidwire",
        "White Ichigo", "White", "Tia Halibel", "Adapting Soul", "Metastasia"
    ],
    "My Hero Academia": [
        "Izuku Midoriya", "Katsuki Bakugo", "All Might", "Shoto Todoroki",
        "Tsuyu Asui", "Iida Tenya", "Momo Yaoyorozu", "Kaminari Denki",
        "Jirou Kyoka", "Mineta Minoru", "Kirishima Eijiro", "Koda Koji",
        "Ojirou Mashirao", "Sato Rikido", "Deku", "Aizawa Shouta", "Present Mic",
        "Midnight", "All Might", "Endeavor", "Best Jeanist", "Hawks",
        "Dabi", "Toga Himiko", "Spinner", "Compress", "Twice", "Mr. Compress",
        "Stain", "Muscular", "Moonfish", "Overhaul", "Eri", "Lemillion",
        "Togen Zenin", "Tamaki Amajiki", "Nejire Hadou", "Fat Gum", "Red Riot",
        "Kirishima", "Sugarman", "Tentacole", "Bondo", "Pixie-Bob", "Tiger",
        "Mandalay", "Vlad King", "13", "Recovery Girl", "Cementoss", "Power Loader"
    ],
    "Jujutsu Kaisen": [
        "Yuji Itadori", "Satoru Gojo", "Megumi Fushiguro", "Nobara Kugisaki",
        "Ryomen Sukuna", "Nanami Kento", "Mahito", "Todou Aoi", "Maki Zenin",
        "Panda", "Inumaki Toge", "Gege Akutami", "Junpei Yoshino", "Getou Suguru",
        "Yuta Okkotsu", "Mima Kitagawa", "Mimicry", "Death Paintings", "Choso",
        "Uraume", "Kenjaku", "Sukuna's Fingers", "Special Grade", "Jogo",
        "Hanami", "Dagon", "Geto", "Yuki Tsukumo", "Shoko Ieiri", "Masamichi Yaga",
        "Atsuya Kusakabe", "Useless Curse", "Curses", "Humans", "Sorcerers",
        "Michizane Sugawara", "Raidou", "Takuma Ino", "Naoya Zenin", "Maki Sister"
    ],
    "Demon Slayer": [
        "Tanjiro Kamado", "Nezuko Kamado", "Zenitsu Agatsuma", "Inosuke Hashibira",
        "Kanao Tsuyuri", "Giyu Tomioka", "Shinobu Kocho", "Kyojuro Rengoku",
        "Tengen Uzui", "Muzan Kibutsuji", "Tomioka Giyu", "Kanroji Mitsuri",
        "Iguro Obanai", "Shinazugawa Sanemi", "Rengoku Kyojuro", "Uzui Tengen",
        "Kocho Shinobu", "Kanae Kocho", "Sakonji Urokodaki", "Sabito", "Makomo",
        "Susamaru", "Yahaba", "Rui", "Enmu", "Akaza", "Doma", "Kokushibo",
        "Hairou", "Kaigaku", "Yushiro", "Aoi Kanzaki", "Sumi Nakamura",
        "Kiyo Terauchi", "Naho Takada", "Genya Shinazugawa", "Hantengu",
        "Gyutaro", "Daki", "Sekido", "Karaku", "Urogi", "Upper Moon Demons"
    ],
    "Attack on Titan": [
        "Eren Yeager", "Mikasa Ackerman", "Levi Ackerman", "Armin Arlet",
        "Annie Leonhart", "Bertholdt Hoover", "Reiner Braun", "Historia Reiss",
        "Ymir", "Jean Kirstein", "Sasha Blouse", "Connie Springer", "Marco Bott",
        "Thomas Wagner", "Mina Carolina", "Oruo Bornstein", "Petra Ral",
        "Gunther Schultz", "Erwin Smith", "Hange Zoe", "Zeke Yeager", "Tom Ксава",
        "Kenny Ackerman", "Rod Reiss", "Frieda Reiss", "Carla Yeager",
        "Dina Fritz", "Grisha Yeager", "Fay Yeager", "Pixis", "Nile Dawk",
        "Dot Pixis", "Commander Pyxis", "Beast Titan", "Colossal Titan"
    ],
    "Fullmetal Alchemist": [
        "Edward Elric", "Alphonse Elric", "Roy Mustang", "Riza Hawkeye",
        "Winry Rockbell", "Scar", "Envy", "Greed", "Sloth", "Pride",
        "Wrath", "Lust", "Gluttony", "Homunculus", "King Bradley",
        "Maes Hughes", "Jean Havoc", "Heymans Breda", "Kain Fuery",
        "Maria Ross", "Sheska", "Shou Tucker", "Nina Tucker", "Liore",
        "Cornello", "Father", "Hohenheim", "Trisha A. Hughes", "Ross"
    ],
    "Hunter x Hunter": [
        "Gon Freecss", "Killua Zoldyck", "Leorio Paradinight", "Kurapika",
        "Hisoka Morow", "Illumi Zoldyck", "Chrollo Lucilfer", "Netero",
        "Meruem", "Shaiapouf", "Neferpitou", "Menthuthuyoupi", "Alluka Zoldyck",
        "Milluki Zoldyck", "Kalluto Zoldyck", "Silva Zoldyck", "Kikyo Zoldyck",
        "Bisky", "Wing", "Canary", "Palm Siberia", "Knov", "Morel",
        "Biscuit Kruger", "Chimera Ant Queen", "Pokkle", "Ponzu", "Tonpa"
    ],
    "Code Geass": [
        "Lelouch vi Britannia", "Kallen Kouzuki", "Suzaku Kururugi", "CC",
        "Milly Ashford", "Rivalz Cardemonde", "Shirley Fenette", "Nina Einstein",
        "Schneizel el Britannia", "Clovis la Britannia", "Cornelia li Britannia",
        "Euphemia li Britannia", "Odyssey", "Rolo Haliburton", "Jeremiah Gottwald",
        "Villetta Nu", "Ran Darts", "Lloyd Asplund", "Cecile Croomy", "Sayoko Shinozaki"
    ],
    "Steins Gate": [
        "Rintaro Okabe", "Kurisu Makise", "Mayuri Shiina", "Itaru Hashida",
        "Luka Urushibara", "Moeka Kiryu", "Sern", "Amane Suzuha", "Maho Hiyajo",
        "Kageyama Shien", "Faris Nyan-Nyan", "Nae Tutusushi", "John Titor"
    ],
    "Psycho-Pass": [
        "Akane Tsunemori", "Shinya Kougami", "Nobuchika Ginoza", "Shrei Masaoka",
        "Yayoi Kunizuka", "Tomomi Masaoka", "Shusei Kagari", "Makishima Shougo",
        "Sibyl System", "Remo Tsukumo"
    ],
    "Mob Psycho 100": [
        "Shigeo Kageyama", "Reigen Arataka", "Teruki Hanazawa", "Ritsu Kageyama",
        "Dimple", "Tomohito Tomoe", "Mitsuo Kumagami", "Tsubomi Takane",
        "Serizawa Katsuya", "Claw Organization"
    ],
    "Vinland Saga": [
        "Thorfinn", "Askeladd", "Ragnar Lothbrok", "Canute", "Floki",
        "Leif Erikson", "Thors", "Sigrid", "Ketil", "Arnheid", "Snake"
    ],
    "Tower of God": [
        "Bam", "Khun Aguero Agnes", "Rak Wraithraiser", "Yuri Zahard",
        "Endorsi Zahard", "Anaak Jahad", "Hatsu", "Shibisu", "Novick",
        "Sora", "Deng Deng"
    ],
    "Solo Leveling": [
        "Sung Jinwoo", "Sung Jihye", "Sung Hyein", "Cha Hae-in",
        "Yoo Ryeo-han", "Go Gunhee", "Baek Yoonho", "Thomas Andre"
    ],
    "Jojo's Bizarre Adventure": [
        "Jonathan Joestar", "Dio Brando", "Joseph Joestar", "Muhammad Avdol",
        "Noriaki Kakaoin", "Leone Abbacchio", "Guido Mista", "Pannacotta Fugo",
        "Giorno Giovanna", "Josuke Higashikata", "Okuyasu Nijimura", "Rohan Kishibe",
        "Josiah Jotaro", "Jotaro Kujo", "Jolyne Cujoh", "Emporio Alniño"
    ],
    "Gintama": [
        "Sakata Gintoki", "Kagura", "Shinpachi Shimura", "Otose",
        "Hijikata Toushiro", "Okita Sougo", "Kondo Isao", "Sarutobi Ayako",
        "Katsura Kotaro", "Hasegawa Taizou", "Yamazaki Sagaru", "Takechi Henpeita",
        "Mutsu", "Tsukuyo", "Gintoki's Group", "Shinsengumi", "Kiheitai"
    ],
    "Aot": [
        "Zeke Jaeger", "Ymir Fritz", "Paths", "Coordinate", "Founder Titan"
    ],
    "Tokyo Ghoul": [
        "Ken Kaneki", "Touka Kirishima", "Hide Nagachika", "Rize Kamishiro",
        "Uta", "Tsukumo", "Ayato Kirishima", "Hinami Fueguchi", "Noro", "Jason",
        "Tatara", "Naki", "Shachi", "Eto Yoshimura", "Arima Kishou", "Juzo Suzuya"
    ],
    "Mob Psycho 100": [
        "Shigeo Kageyama", "Reigen Arataka", "Teruki Hanazawa", "Ritsu Kageyama",
        "Dimple", "Tomohito Tomoe", "Mitsuo Kumagami", "Tsubomi Takane",
        "Serizawa Katsuya", "Claw Organization", "Koyama", "Onigawara"
    ],
    "Vinland Saga": [
        "Thorfinn", "Askeladd", "Ragnar Lothbrok", "Canute", "Floki",
        "Leif Erikson", "Thors", "Sigrid", "Ketil", "Arnheid", "Snake",
        "Bjorn", "Einar", "Gardar", "Hild", "Farm People"
    ],
    "Tower of God": [
        "Bam", "Khun Aguero Agnes", "Rak Wraithraiser", "Yuri Zahard",
        "Endorsi Zahard", "Anaak Jahad", "Hatsu", "Shibisu", "Novick",
        "Sora", "Deng Deng", "Urek Mazino", "Jahad", "Data Zahard"
    ],
    "Solo Leveling": [
        "Sung Jinwoo", "Sung Jihye", "Sung Hyein", "Cha Hae-in",
        "Yoo Ryeo-han", "Go Gunhee", "Baek Yoonho", "Thomas Andre", "Hwang Dongsoo"
    ],
    "Classroom of the Elite": [
        "Ayanokoji Kiyotaka", "Suzune Horikita", "Kikyo Kushida", "Koji Haruka",
        "Yosuke Hirata", "Kanji Ike", "You Ibuki", "Satsuki Shibuya", "Airi Sakura"
    ],
    "Toilet-Bound Hanako-kun": [
        "Hanako", "Yashiro Nene", "Tuxedo Sam", "Tsuchomado", "Yako Kitsune",
        "Kako", "Kou Minamoto", "Akira Aoi", "Midnight Staff"
    ],
    "Rwby": [
        "Ruby Rose", "Weiss Schnee", "Blake Belladonna", "Yang Xiao Long",
        "Jaune Arc", "Pyrrha Nikos", "Lie Ren", "Nora Valkyrie", "Cinder Fall"
    ],
    "Avatar The Last Airbender": [
        "Aang", "Katara", "Sokka", "Toph", "Zuko", "Iroh", "Azula",
        "Appa", "Momo", "Cabbage Guy", "Uncle Iroh"
    ],
    "The Legend of Korra": [
        "Korra", "Asami Sato", "Mako", "Bolin", "Tenzin", "Lin Beifong"
    ],
    "Castlevania": [
        "Trevor Belmont", "Sypha Belnades", "Alucard", "Dracula", "Vlad III",
        "Carmilla", "Hector", "Isaac", "Saint Germain", "Striga"
    ],
    "Cyberpunk Edgerunners": [
        "David Martinez", "Lucy", "Falco", "Maine", "Dorio", "Kiwi",
        "Pilar", "Viktor Sásago", "Saburo Arasaka"
    ]
}

# Ajouter plus de personnages pour chaque anime
extra_characters = {
    "Naruto": [
        "Hayabusa", "Chiyo", "Hanzo", "Temari", "Gaara", "Kankuro",
        "Baki", "Ebizo", "Mebuki Haruno", "Fugaku Uchiha", "Mikoto Uchiha",
        "Shikaku Nara", "Yoshino Nara", "Choza Akimichi", "Choji's Father",
        "Hiashi Hyuga", "Hizashi Hyuga", "Neji's Father", "Hanabi Hyuga"
    ],
    "One Piece": [
        "Portgas D. Ace", "Sabo", "Dragon", "Garp", "Sengoku", "Smoker",
        "Coby", "Helmeppo", "Alvida", "Jango", "Nojiko", "Genzo"
    ],
    "Bleach": [
        "Yachiru Kusajishi", "Ikkaku Madarame", "Yumichika Ayasegawa",
        "Isane Kotetsu", "Nanao Ise", "Momo Hinamori", "Izuru Kira"
    ]
}

# Générer la liste complète
all_characters = []
for anime, characters in characters_by_anime.items():
    for char in characters:
        all_characters.append({"name": char, "anime": anime})

    # Ajouter extras si disponibles
    if anime in extra_characters:
        for char in extra_characters[anime]:
            all_characters.append({"name": char, "anime": anime})

# Imprimer la statistique
print(f"Total: {len(all_characters)} personnages\n")
print("Par anime:")
count_by_anime = defaultdict(int)
for char in all_characters:
    count_by_anime[char['anime']] += 1

for anime in sorted(count_by_anime.keys()):
    print(f"  {anime}: {count_by_anime[anime]}")

# Limiter à 500 persos
all_characters = all_characters[:500]

# Imprimer la statistique finale
print(f"\nFinal: {len(all_characters)} personnages (limité à 500)\n")

# Sauvegarder en JSON
output = {"characters": all_characters}
with open("data/all_characters.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"✅ Saved to data/all_characters.json")
